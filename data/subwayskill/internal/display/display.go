package display

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"subwayskill/internal/feed"
)

// StationResult groups departures for a single station.
type StationResult struct {
	StationName string
	StopID      string
	Routes      []string
	NorthLabel  string
	SouthLabel  string
	Departures  []feed.Departure
	Source      string // "realtime" or "scheduled"
	SourceNote  string // extra info about schedule source
}

// FormatText renders station results as LLM-friendly text.
func FormatText(results []StationResult, queryTime time.Time, targetTime *time.Time) string {
	var b strings.Builder

	source := "realtime"
	for _, r := range results {
		if r.Source == "scheduled" {
			source = "scheduled"
			break
		}
	}

	loc := queryTime.Location()
	b.WriteString(fmt.Sprintf("=== NYC Subway Departures (%s) ===\n", source))
	if targetTime != nil {
		b.WriteString(fmt.Sprintf("Target time: %s\n", targetTime.In(loc).Format("2006-01-02 15:04 MST")))
	} else {
		b.WriteString(fmt.Sprintf("Query time: %s\n", queryTime.In(loc).Format("2006-01-02 15:04 MST")))
	}

	for _, result := range results {
		routeStr := strings.Join(result.Routes, ", ")
		b.WriteString(fmt.Sprintf("\n--- %s (%s) ---\n", result.StationName, routeStr))

		if len(result.Departures) == 0 {
			b.WriteString("  No upcoming departures found\n")
			continue
		}

		// Group by route and direction
		type groupKey struct {
			Route     string
			Direction string
		}
		groups := make(map[groupKey][]feed.Departure)
		var order []groupKey

		for _, d := range result.Departures {
			key := groupKey{Route: d.Route, Direction: d.Direction}
			if _, exists := groups[key]; !exists {
				order = append(order, key)
			}
			groups[key] = append(groups[key], d)
		}

		for _, key := range order {
			deps := groups[key]
			dirLabel := "northbound"
			if key.Direction == "S" {
				dirLabel = "southbound"
			}

			// Add destination label if available
			destLabel := ""
			if key.Direction == "N" && result.NorthLabel != "" {
				destLabel = fmt.Sprintf(" (%s)", result.NorthLabel)
			} else if key.Direction == "S" && result.SouthLabel != "" {
				destLabel = fmt.Sprintf(" (%s)", result.SouthLabel)
			}

			var timeStrs []string
			for _, d := range deps {
				mins := int(time.Until(d.Time).Minutes())
				if targetTime != nil {
					// For scheduled, just show absolute times
					timeStrs = append(timeStrs, d.Time.In(loc).Format("15:04"))
				} else if mins <= 0 {
					timeStrs = append(timeStrs, fmt.Sprintf("now (%s)", d.Time.In(loc).Format("15:04")))
				} else {
					timeStrs = append(timeStrs, fmt.Sprintf("%d min (%s)", mins, d.Time.In(loc).Format("15:04")))
				}
			}

			b.WriteString(fmt.Sprintf("  %s %s%s: %s\n",
				key.Route, dirLabel, destLabel, strings.Join(timeStrs, ", ")))
		}

		if result.SourceNote != "" {
			b.WriteString(fmt.Sprintf("  Source: %s\n", result.SourceNote))
		}
	}

	return b.String()
}

// JSONOutput is the structured JSON output format.
type JSONOutput struct {
	Source     string          `json:"source"`
	QueryTime string          `json:"query_time"`
	Stations  []JSONStation   `json:"stations"`
}

type JSONStation struct {
	Name       string          `json:"name"`
	StopID     string          `json:"stop_id"`
	Routes     []string        `json:"routes"`
	Source     string          `json:"source"`
	SourceNote string          `json:"source_note,omitempty"`
	Departures []JSONDeparture `json:"departures"`
}

type JSONDeparture struct {
	Route     string `json:"route"`
	Direction string `json:"direction"`
	DirLabel  string `json:"direction_label"`
	Time      string `json:"time"`
	MinAway   int    `json:"minutes_away"`
}

// FormatJSON renders station results as JSON.
func FormatJSON(results []StationResult, queryTime time.Time) (string, error) {
	loc := queryTime.Location()

	source := "realtime"
	for _, r := range results {
		if r.Source == "scheduled" {
			source = "scheduled"
			break
		}
	}

	output := JSONOutput{
		Source:    source,
		QueryTime: queryTime.In(loc).Format(time.RFC3339),
	}

	for _, result := range results {
		js := JSONStation{
			Name:       result.StationName,
			StopID:     result.StopID,
			Routes:     result.Routes,
			Source:     result.Source,
			SourceNote: result.SourceNote,
		}

		for _, d := range result.Departures {
			dirLabel := "northbound"
			if d.Direction == "S" {
				dirLabel = "southbound"
			}

			mins := int(time.Until(d.Time).Minutes())
			if mins < 0 {
				mins = 0
			}

			js.Departures = append(js.Departures, JSONDeparture{
				Route:     d.Route,
				Direction: d.Direction,
				DirLabel:  dirLabel,
				Time:      d.Time.In(loc).Format(time.RFC3339),
				MinAway:   mins,
			})
		}

		output.Stations = append(output.Stations, js)
	}

	data, err := json.MarshalIndent(output, "", "  ")
	if err != nil {
		return "", err
	}
	return string(data), nil
}
