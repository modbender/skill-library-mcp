package schedule

import (
	"archive/zip"
	"bytes"
	"encoding/csv"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"subwayskill/internal/feed"
)

const (
	regularGTFSURL      = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip"
	supplementedGTFSURL = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_supplemented.zip"
	regularCacheTTL     = 24 * time.Hour
	supplementedCacheTTL = 1 * time.Hour
)

func cacheDir() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".cache", "subwayskill")
}

// GetScheduledDepartures returns scheduled departures for a stop, route, and direction
// around the target time within the given window (in minutes).
func GetScheduledDepartures(stopID string, routes []string, direction string, targetTime time.Time, windowMin int) ([]feed.Departure, string, error) {
	// Try supplemented first (more accurate for near-term), fall back to regular
	deps, note, err := getFromGTFS(supplementedGTFSURL, "gtfs_supplemented.zip", supplementedCacheTTL,
		stopID, routes, direction, targetTime, windowMin)
	if err == nil && len(deps) > 0 {
		return deps, note, nil
	}

	deps, note, err = getFromGTFS(regularGTFSURL, "gtfs_subway.zip", regularCacheTTL,
		stopID, routes, direction, targetTime, windowMin)
	if err != nil {
		return nil, "", fmt.Errorf("fetching schedule: %w", err)
	}
	return deps, note, nil
}

func getFromGTFS(url, filename string, ttl time.Duration, stopID string, routes []string, direction string, targetTime time.Time, windowMin int) ([]feed.Departure, string, error) {
	data, err := getCachedOrDownload(url, filename, ttl)
	if err != nil {
		return nil, "", err
	}

	deps, err := parseGTFSZip(data, stopID, routes, direction, targetTime, windowMin)
	if err != nil {
		return nil, "", err
	}

	note := "Regular GTFS"
	if strings.Contains(filename, "supplemented") {
		note = "Supplemented GTFS"
	}

	return deps, note, nil
}

func getCachedOrDownload(url, filename string, ttl time.Duration) ([]byte, error) {
	dir := cacheDir()
	cachePath := filepath.Join(dir, filename)

	// Check cache
	if info, err := os.Stat(cachePath); err == nil {
		if time.Since(info.ModTime()) < ttl {
			return os.ReadFile(cachePath)
		}
	}

	// Download
	fmt.Fprintf(os.Stderr, "Downloading %s...\n", filename)
	client := &http.Client{Timeout: 60 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("downloading %s: %w", filename, err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("downloading %s: status %d", filename, resp.StatusCode)
	}

	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("reading %s: %w", filename, err)
	}

	// Cache it
	if err := os.MkdirAll(dir, 0o755); err == nil {
		_ = os.WriteFile(cachePath, data, 0o644)
	}

	return data, nil
}

func parseGTFSZip(data []byte, stopID string, routes []string, direction string, targetTime time.Time, windowMin int) ([]feed.Departure, error) {
	r, err := zip.NewReader(bytes.NewReader(data), int64(len(data)))
	if err != nil {
		return nil, fmt.Errorf("opening zip: %w", err)
	}

	// Step 1: Find trips for our routes that run on the target day
	validTrips, err := findValidTrips(r, routes, targetTime)
	if err != nil {
		return nil, err
	}

	if len(validTrips) == 0 {
		return nil, nil
	}

	// Step 2: Find stop times for our stop on those trips
	departures, err := findStopTimes(r, validTrips, stopID, direction, targetTime, windowMin)
	if err != nil {
		return nil, err
	}

	return departures, nil
}

// tripInfo stores route_id and direction_id for a trip.
type tripInfo struct {
	routeID     string
	directionID string
}

func findValidTrips(r *zip.Reader, routes []string, targetTime time.Time) (map[string]tripInfo, error) {
	routeSet := make(map[string]bool)
	for _, rt := range routes {
		routeSet[strings.ToUpper(rt)] = true
	}

	// Parse calendar.txt to find service IDs active on the target day
	activeServices, err := getActiveServices(r, targetTime)
	if err != nil {
		return nil, err
	}

	// Parse trips.txt
	tripsFile, err := openZipFile(r, "trips.txt")
	if err != nil {
		return nil, err
	}

	reader := csv.NewReader(tripsFile)
	header, err := reader.Read()
	if err != nil {
		return nil, fmt.Errorf("reading trips.txt header: %w", err)
	}

	idx := csvIndex(header)
	validTrips := make(map[string]tripInfo)

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			continue
		}

		routeID := strings.ToUpper(record[idx["route_id"]])
		if len(routeSet) > 0 && !routeSet[routeID] {
			continue
		}

		serviceID := record[idx["service_id"]]
		if !activeServices[serviceID] {
			continue
		}

		tripID := record[idx["trip_id"]]
		dirID := ""
		if i, ok := idx["direction_id"]; ok {
			dirID = record[i]
		}

		validTrips[tripID] = tripInfo{
			routeID:     routeID,
			directionID: dirID,
		}
	}

	return validTrips, nil
}

func getActiveServices(r *zip.Reader, targetTime time.Time) (map[string]bool, error) {
	active := make(map[string]bool)
	dateStr := targetTime.Format("20060102")
	dayOfWeek := strings.ToLower(targetTime.Weekday().String())

	// Parse calendar.txt
	calFile, err := openZipFile(r, "calendar.txt")
	if err == nil {
		reader := csv.NewReader(calFile)
		header, err := reader.Read()
		if err == nil {
			idx := csvIndex(header)
			for {
				record, err := reader.Read()
				if err == io.EOF {
					break
				}
				if err != nil {
					continue
				}

				serviceID := record[idx["service_id"]]
				startDate := record[idx["start_date"]]
				endDate := record[idx["end_date"]]

				if dateStr < startDate || dateStr > endDate {
					continue
				}

				if dayIdx, ok := idx[dayOfWeek]; ok && record[dayIdx] == "1" {
					active[serviceID] = true
				}
			}
		}
	}

	// Parse calendar_dates.txt for exceptions
	cdFile, err := openZipFile(r, "calendar_dates.txt")
	if err == nil {
		reader := csv.NewReader(cdFile)
		header, err := reader.Read()
		if err == nil {
			idx := csvIndex(header)
			for {
				record, err := reader.Read()
				if err == io.EOF {
					break
				}
				if err != nil {
					continue
				}

				if record[idx["date"]] != dateStr {
					continue
				}

				serviceID := record[idx["service_id"]]
				exType := record[idx["exception_type"]]

				if exType == "1" {
					active[serviceID] = true
				} else if exType == "2" {
					delete(active, serviceID)
				}
			}
		}
	}

	return active, nil
}

func findStopTimes(r *zip.Reader, validTrips map[string]tripInfo, stopID, direction string, targetTime time.Time, windowMin int) ([]feed.Departure, error) {
	stFile, err := openZipFile(r, "stop_times.txt")
	if err != nil {
		return nil, err
	}

	reader := csv.NewReader(stFile)
	header, err := reader.Read()
	if err != nil {
		return nil, fmt.Errorf("reading stop_times.txt header: %w", err)
	}

	idx := csvIndex(header)

	// Build target stop IDs
	targetStops := make(map[string]string) // full stop ID -> direction
	if direction == "" || direction == "N" {
		targetStops[stopID+"N"] = "N"
	}
	if direction == "" || direction == "S" {
		targetStops[stopID+"S"] = "S"
	}
	// Some feeds use just the base ID
	if direction == "" {
		targetStops[stopID] = ""
	}

	// Time window
	windowBefore := time.Duration(windowMin/2) * time.Minute
	windowAfter := time.Duration(windowMin/2+windowMin%2) * time.Minute
	windowStart := targetTime.Add(-windowBefore)
	windowEnd := targetTime.Add(windowAfter)

	loc := targetTime.Location()
	baseDate := time.Date(targetTime.Year(), targetTime.Month(), targetTime.Day(), 0, 0, 0, 0, loc)

	var departures []feed.Departure

	for {
		record, err := reader.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			continue
		}

		tripID := record[idx["trip_id"]]
		trip, ok := validTrips[tripID]
		if !ok {
			continue
		}

		sid := record[idx["stop_id"]]
		dir, ok := targetStops[sid]
		if !ok {
			continue
		}

		// If direction wasn't determined by stop suffix, try from trip
		if dir == "" {
			if trip.directionID == "0" {
				dir = "N" // convention: 0 = north/inbound
			} else {
				dir = "S"
			}
		}

		// Parse departure time (can be > 24:00:00 for overnight trips)
		depTimeStr := record[idx["departure_time"]]
		depTime, err := parseGTFSTime(depTimeStr, baseDate)
		if err != nil {
			continue
		}

		if depTime.Before(windowStart) || depTime.After(windowEnd) {
			continue
		}

		departures = append(departures, feed.Departure{
			Route:     trip.routeID,
			Direction: dir,
			Time:      depTime,
			StopID:    sid,
		})
	}

	sort.Slice(departures, func(i, j int) bool {
		return departures[i].Time.Before(departures[j].Time)
	})

	return departures, nil
}

// parseGTFSTime parses a GTFS time string (HH:MM:SS, can exceed 24h) relative to a base date.
func parseGTFSTime(s string, baseDate time.Time) (time.Time, error) {
	parts := strings.Split(strings.TrimSpace(s), ":")
	if len(parts) != 3 {
		return time.Time{}, fmt.Errorf("invalid time: %s", s)
	}

	var h, m, sec int
	if _, err := fmt.Sscanf(parts[0], "%d", &h); err != nil {
		return time.Time{}, err
	}
	if _, err := fmt.Sscanf(parts[1], "%d", &m); err != nil {
		return time.Time{}, err
	}
	if _, err := fmt.Sscanf(parts[2], "%d", &sec); err != nil {
		return time.Time{}, err
	}

	return baseDate.Add(time.Duration(h)*time.Hour + time.Duration(m)*time.Minute + time.Duration(sec)*time.Second), nil
}

func openZipFile(r *zip.Reader, name string) (io.Reader, error) {
	for _, f := range r.File {
		if f.Name == name || strings.HasSuffix(f.Name, "/"+name) {
			rc, err := f.Open()
			if err != nil {
				return nil, fmt.Errorf("opening %s: %w", name, err)
			}
			return rc, nil
		}
	}
	return nil, fmt.Errorf("%s not found in zip", name)
}

func csvIndex(header []string) map[string]int {
	idx := make(map[string]int)
	for i, h := range header {
		idx[strings.TrimSpace(h)] = i
	}
	return idx
}
