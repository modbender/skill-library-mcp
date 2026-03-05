package cmd

import (
	"fmt"
	"os"
	"strings"
	"sync"
	"time"

	"subwayskill/internal/display"
	"subwayskill/internal/feed"
	"subwayskill/internal/schedule"
	"subwayskill/internal/station"

	"github.com/spf13/cobra"
)

var (
	direction string
	timeFlag  string
	window    int
	jsonOut   bool
)

type stationQuery struct {
	name       string
	stopID     string
	routes     []string
	northLabel string
	southLabel string
}

var rootCmd = &cobra.Command{
	Use:   "subwayskill [LINE] [STATION]",
	Short: "NYC subway departure times",
	Long:  "Fetches NYC subway departure times for specific stations. Defaults to Clinton-Washington (C), Bergen (2,3), 7 Av (Q), Atlantic Av (4,5).",
	Args:  cobra.MaximumNArgs(2),
	RunE:  run,
}

func init() {
	rootCmd.Flags().StringVarP(&direction, "direction", "d", "", "filter direction: N (northbound) or S (southbound)")
	rootCmd.Flags().StringVarP(&timeFlag, "time", "t", "", "target departure time (HH:MM), default: now")
	rootCmd.Flags().IntVarP(&window, "window", "w", 0, "minutes of departures to show (default: 30 for schedule, all for realtime)")
	rootCmd.Flags().BoolVar(&jsonOut, "json", false, "output as JSON")
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func run(cmd *cobra.Command, args []string) error {
	now := time.Now()
	loc := now.Location()

	// Validate direction
	if direction != "" {
		direction = strings.ToUpper(direction)
		if direction != "N" && direction != "S" {
			return fmt.Errorf("direction must be N or S, got %q", direction)
		}
	}

	// Parse target time
	var targetTime *time.Time
	useSchedule := false

	if timeFlag != "" {
		t, err := time.ParseInLocation("15:04", timeFlag, loc)
		if err != nil {
			return fmt.Errorf("invalid time %q (expected HH:MM): %w", timeFlag, err)
		}
		// Set to today's date
		target := time.Date(now.Year(), now.Month(), now.Day(), t.Hour(), t.Minute(), 0, 0, loc)
		// If the time is in the past, assume tomorrow
		if target.Before(now) {
			target = target.Add(24 * time.Hour)
		}
		targetTime = &target

		// If target is more than 5 minutes in the future, we may need schedule
		if target.Sub(now) > 5*time.Minute {
			useSchedule = true
		}
	}

	// Determine which stations to query
	var queries []stationQuery

	if len(args) >= 1 {
		// Specific line/station
		route := strings.ToUpper(args[0])

		// Validate route
		if !station.IsValidRoute(route) {
			return fmt.Errorf("unknown line %q. Valid lines: 1 2 3 4 5 6 7 A C E B D F M G J Z L N Q R W S SIR", route)
		}

		if len(args) >= 2 {
			nameQuery := args[1]
			s, err := station.Lookup(route, nameQuery)
			if err != nil {
				return err
			}
			queries = append(queries, stationQuery{
				name:       s.Name,
				stopID:     s.StopID,
				routes:     s.Routes,
				northLabel: s.NorthLabel,
				southLabel: s.SouthLabel,
			})
		} else {
			// Just a line, no station — show defaults that serve this line
			defaults := station.Defaults()
			found := false
			for _, d := range defaults {
				for _, r := range d.FeedRoutes {
					if r == route {
						queries = append(queries, stationQuery{
							name:       d.Name,
							stopID:     d.StopID,
							routes:     []string{route},
							northLabel: d.NorthLabel,
							southLabel: d.SouthLabel,
						})
						found = true
					}
				}
			}
			if !found {
				return fmt.Errorf("line %s is valid but not in default stations. Specify a station: subwayskill %s <station-name>", route, route)
			}
		}
	} else {
		// No args — all defaults
		for _, d := range station.Defaults() {
			queries = append(queries, stationQuery{
				name:       d.Name,
				stopID:     d.StopID,
				routes:     d.FeedRoutes,
				northLabel: d.NorthLabel,
				southLabel: d.SouthLabel,
			})
		}
	}

	// Fetch departures
	var results []display.StationResult

	if useSchedule {
		// Try realtime first, fall back to schedule
		results = fetchWithScheduleFallback(queries, targetTime, now)
	} else {
		// Realtime only
		results = fetchRealtime(queries, now)
	}

	// Output
	if jsonOut {
		out, err := display.FormatJSON(results, now)
		if err != nil {
			return fmt.Errorf("formatting JSON: %w", err)
		}
		fmt.Println(out)
	} else {
		fmt.Print(display.FormatText(results, now, targetTime))
	}

	return nil
}

func fetchRealtime(queries []stationQuery, now time.Time) []display.StationResult {
	type result struct {
		idx int
		sr  display.StationResult
	}

	results := make([]display.StationResult, len(queries))
	ch := make(chan result, len(queries))
	var wg sync.WaitGroup

	for i, q := range queries {
		wg.Add(1)
		go func(idx int, q stationQuery) {
			defer wg.Done()

			var allDeps []feed.Departure
			feedMap := feed.FeedURLsForRoutes(q.routes)

			for url, routes := range feedMap {
				deps, err := feed.FetchDepartures(url, q.stopID, routes, direction)
				if err != nil {
					fmt.Fprintf(os.Stderr, "Warning: feed error for %s: %v\n", q.name, err)
					continue
				}
				allDeps = append(allDeps, deps...)
			}

			ch <- result{
				idx: idx,
				sr: display.StationResult{
					StationName: q.name,
					StopID:      q.stopID,
					Routes:      q.routes,
					NorthLabel:  q.northLabel,
					SouthLabel:  q.southLabel,
					Departures:  allDeps,
					Source:      "realtime",
				},
			}
		}(i, q)
	}

	go func() {
		wg.Wait()
		close(ch)
	}()

	for r := range ch {
		results[r.idx] = r.sr
	}

	return results
}

func fetchWithScheduleFallback(queries []stationQuery, targetTime *time.Time, now time.Time) []display.StationResult {
	results := make([]display.StationResult, len(queries))

	for i, q := range queries {
		// Try realtime first
		var allDeps []feed.Departure
		feedMap := feed.FeedURLsForRoutes(q.routes)

		for url, routes := range feedMap {
			deps, err := feed.FetchDepartures(url, q.stopID, routes, direction)
			if err != nil {
				continue
			}
			allDeps = append(allDeps, deps...)
		}

		// Filter realtime to time window around target
		w := window
		if w == 0 {
			w = 30
		}
		halfWindow := time.Duration(w/2) * time.Minute
		var filtered []feed.Departure
		for _, d := range allDeps {
			if d.Time.After(targetTime.Add(-halfWindow)) && d.Time.Before(targetTime.Add(halfWindow)) {
				filtered = append(filtered, d)
			}
		}

		if len(filtered) > 0 {
			results[i] = display.StationResult{
				StationName: q.name,
				StopID:      q.stopID,
				Routes:      q.routes,
				NorthLabel:  q.northLabel,
				SouthLabel:  q.southLabel,
				Departures:  filtered,
				Source:      "realtime",
			}
			continue
		}

		// Fall back to schedule
		deps, sourceNote, err := schedule.GetScheduledDepartures(q.stopID, q.routes, direction, *targetTime, w)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Warning: schedule error for %s: %v\n", q.name, err)
		}

		results[i] = display.StationResult{
			StationName: q.name,
			StopID:      q.stopID,
			Routes:      q.routes,
			NorthLabel:  q.northLabel,
			SouthLabel:  q.southLabel,
			Departures:  deps,
			Source:      "scheduled",
			SourceNote:  sourceNote,
		}
	}

	return results
}
