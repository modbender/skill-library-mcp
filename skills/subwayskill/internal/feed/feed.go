package feed

import (
	"fmt"
	"io"
	"net/http"
	"sort"
	"strings"
	"time"

	"github.com/MobilityData/gtfs-realtime-bindings/golang/gtfs"
	"google.golang.org/protobuf/proto"
)

// feedURLs maps route IDs to their GTFS-RT feed URLs.
var feedURLs = map[string]string{
	"1": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"2": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"3": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"4": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"5": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"6": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"7": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"S": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
	"A": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
	"C": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
	"E": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
	"B": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
	"D": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
	"F": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
	"M": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
	"N": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
	"Q": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
	"R": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
	"W": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
	"G":   "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
	"J":   "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
	"Z":   "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
	"L":   "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
	"SIR": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-si",
}

// Departure represents a single train departure.
type Departure struct {
	Route     string
	Direction string // "N" or "S"
	Time      time.Time
	StopID    string
}

// FeedURL returns the GTFS-RT feed URL for a given route.
func FeedURL(route string) (string, error) {
	url, ok := feedURLs[strings.ToUpper(route)]
	if !ok {
		return "", fmt.Errorf("unknown route: %s", route)
	}
	return url, nil
}

// FeedURLsForRoutes returns deduplicated feed URLs for a set of routes.
func FeedURLsForRoutes(routes []string) map[string][]string {
	// url -> routes served by that feed
	result := make(map[string][]string)
	for _, r := range routes {
		url, err := FeedURL(r)
		if err != nil {
			continue
		}
		result[url] = append(result[url], r)
	}
	return result
}

// FetchDepartures fetches realtime departures for a stop from a feed URL,
// filtered by the given routes and optional direction.
func FetchDepartures(feedURL, stopID string, routes []string, direction string) ([]Departure, error) {
	body, err := fetchFeed(feedURL)
	if err != nil {
		return nil, err
	}
	return parseDepartures(body, stopID, routes, direction)
}

func fetchFeed(url string) ([]byte, error) {
	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("fetching feed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("feed returned status %d", resp.StatusCode)
	}

	return io.ReadAll(resp.Body)
}

func parseDepartures(data []byte, stopID string, routes []string, direction string) ([]Departure, error) {
	feed := &gtfs.FeedMessage{}
	if err := proto.Unmarshal(data, feed); err != nil {
		return nil, fmt.Errorf("parsing feed: %w", err)
	}

	routeSet := make(map[string]bool)
	for _, r := range routes {
		routeSet[strings.ToUpper(r)] = true
	}

	now := time.Now()
	var departures []Departure

	for _, entity := range feed.Entity {
		tu := entity.GetTripUpdate()
		if tu == nil {
			continue
		}

		routeID := tu.GetTrip().GetRouteId()
		if len(routeSet) > 0 && !routeSet[strings.ToUpper(routeID)] {
			continue
		}

		for _, stu := range tu.GetStopTimeUpdate() {
			sid := stu.GetStopId()
			if !matchesStop(sid, stopID, direction) {
				continue
			}

			var depTime time.Time
			if dep := stu.GetDeparture(); dep != nil && dep.GetTime() > 0 {
				depTime = time.Unix(dep.GetTime(), 0)
			} else if arr := stu.GetArrival(); arr != nil && arr.GetTime() > 0 {
				depTime = time.Unix(arr.GetTime(), 0)
			} else {
				continue
			}

			// Skip trains that have already left
			if depTime.Before(now.Add(-1 * time.Minute)) {
				continue
			}

			dir := "N"
			if strings.HasSuffix(sid, "S") {
				dir = "S"
			}

			departures = append(departures, Departure{
				Route:     routeID,
				Direction: dir,
				Time:      depTime,
				StopID:    sid,
			})
		}
	}

	sort.Slice(departures, func(i, j int) bool {
		return departures[i].Time.Before(departures[j].Time)
	})

	return departures, nil
}

// matchesStop checks if a stop time's stop ID matches our target.
// stopID is the base (e.g. "A44"), direction is "" or "N"/"S".
// Feed stop IDs have direction suffix: "A44N", "A44S".
func matchesStop(feedStopID, targetBase, direction string) bool {
	if !strings.HasPrefix(feedStopID, targetBase) {
		return false
	}
	suffix := strings.TrimPrefix(feedStopID, targetBase)
	if suffix != "N" && suffix != "S" {
		return false
	}
	if direction != "" && suffix != strings.ToUpper(direction) {
		return false
	}
	return true
}
