package station

import (
	"encoding/csv"
	"fmt"
	"io"
	"strings"

	_ "embed"
)

//go:embed data/stations.csv
var stationsCSV string

// Station represents a subway station with its metadata.
type Station struct {
	StopID          string
	Name            string
	Routes          []string
	NorthLabel      string
	SouthLabel      string
	Line            string
	Borough         string
	DaytimeRoutes   string
}

// DefaultStation is a pre-configured station the tool shows when run with no args.
type DefaultStation struct {
	Station
	FeedRoutes []string // which routes to show from this station
}

// Defaults returns the 4 default stations.
func Defaults() []DefaultStation {
	return []DefaultStation{
		{
			Station: Station{
				StopID:     "A44",
				Name:       "Clinton-Washington Avs",
				Routes:     []string{"C"},
				NorthLabel: "Manhattan-bound",
				SouthLabel: "Euclid Av-bound",
			},
			FeedRoutes: []string{"C"},
		},
		{
			Station: Station{
				StopID:     "236",
				Name:       "Bergen St",
				Routes:     []string{"2", "3"},
				NorthLabel: "Manhattan-bound",
				SouthLabel: "Flatbush Av-bound",
			},
			FeedRoutes: []string{"2", "3"},
		},
		{
			Station: Station{
				StopID:     "D25",
				Name:       "7 Av",
				Routes:     []string{"Q"},
				NorthLabel: "Manhattan-bound",
				SouthLabel: "Coney Island-bound",
			},
			FeedRoutes: []string{"Q"},
		},
		{
			Station: Station{
				StopID:     "235",
				Name:       "Atlantic Av-Barclays Ctr",
				Routes:     []string{"4", "5"},
				NorthLabel: "Manhattan-bound",
				SouthLabel: "Flatbush Av-bound",
			},
			FeedRoutes: []string{"4", "5"},
		},
	}
}

// allStations is the parsed CSV data, lazily loaded.
var allStations []Station

func loadStations() []Station {
	if allStations != nil {
		return allStations
	}

	r := csv.NewReader(strings.NewReader(stationsCSV))
	header, err := r.Read()
	if err != nil {
		return nil
	}

	idx := make(map[string]int)
	for i, h := range header {
		idx[h] = i
	}

	for {
		record, err := r.Read()
		if err == io.EOF {
			break
		}
		if err != nil {
			continue
		}

		routes := strings.Fields(record[idx["Daytime Routes"]])
		s := Station{
			StopID:        record[idx["GTFS Stop ID"]],
			Name:          record[idx["Stop Name"]],
			Routes:        routes,
			NorthLabel:    record[idx["North Direction Label"]],
			SouthLabel:    record[idx["South Direction Label"]],
			Line:          record[idx["Line"]],
			Borough:       record[idx["Borough"]],
			DaytimeRoutes: record[idx["Daytime Routes"]],
		}
		allStations = append(allStations, s)
	}
	return allStations
}

// normalize strips punctuation, lowercases, and collapses spaces for fuzzy matching.
func normalize(s string) string {
	s = strings.ToLower(s)
	var b strings.Builder
	for _, c := range s {
		if c == '-' || c == '/' || c == '\'' {
			b.WriteRune(' ')
		} else if (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == ' ' {
			b.WriteRune(c)
		}
	}
	// collapse multiple spaces
	return strings.Join(strings.Fields(b.String()), " ")
}

// Lookup finds a station by name (fuzzy) that serves the given route.
// Returns the station and which routes at that station to display.
func Lookup(route, nameQuery string) (*Station, error) {
	route = strings.ToUpper(strings.TrimSpace(route))
	query := normalize(nameQuery)

	if query == "" && route == "" {
		return nil, fmt.Errorf("no station or line specified")
	}

	stations := loadStations()

	// Also check defaults for known aliases
	for _, d := range Defaults() {
		if normalize(d.Name) == query || strings.Contains(normalize(d.Name), query) {
			if route == "" || containsRoute(d.Routes, route) {
				s := d.Station
				if route != "" {
					s.Routes = []string{route}
				}
				return &s, nil
			}
		}
	}

	var exactMatches, partialMatches []Station

	for _, s := range stations {
		if route != "" && !containsRoute(s.Routes, route) {
			continue
		}

		normalized := normalize(s.Name)
		if normalized == query {
			match := s
			if route != "" {
				match.Routes = []string{route}
			}
			exactMatches = append(exactMatches, match)
		} else if strings.Contains(normalized, query) {
			match := s
			if route != "" {
				match.Routes = []string{route}
			}
			partialMatches = append(partialMatches, match)
		}
	}

	if len(exactMatches) > 0 {
		return &exactMatches[0], nil
	}
	if len(partialMatches) > 0 {
		return &partialMatches[0], nil
	}

	// Generate suggestions
	suggestions := suggestStations(route, query, stations)
	if len(suggestions) > 0 {
		if route != "" {
			return nil, fmt.Errorf("station %q not found for line %s. Did you mean:\n%s",
				nameQuery, route, formatSuggestions(suggestions))
		}
		return nil, fmt.Errorf("station %q not found. Did you mean:\n%s",
			nameQuery, formatSuggestions(suggestions))
	}

	if route != "" {
		return nil, fmt.Errorf("station %q not found for line %s", nameQuery, route)
	}
	return nil, fmt.Errorf("station %q not found", nameQuery)
}

func containsRoute(routes []string, route string) bool {
	for _, r := range routes {
		if r == route {
			return true
		}
	}
	return false
}

// suggestStations finds stations with similar names or on the same route.
func suggestStations(route, query string, stations []Station) []string {
	var suggestions []string
	seen := make(map[string]bool)

	// First: stations on the same route with any name overlap
	if route != "" {
		for _, s := range stations {
			if !containsRoute(s.Routes, route) {
				continue
			}
			norm := normalize(s.Name)
			queryWords := strings.Fields(query)
			nameWords := strings.Fields(norm)
			for _, qw := range queryWords {
				for _, nw := range nameWords {
					if len(qw) >= 2 && (strings.Contains(nw, qw) || strings.Contains(qw, nw)) {
						if !seen[s.Name] {
							suggestions = append(suggestions, fmt.Sprintf("  %s (%s)", s.Name, s.DaytimeRoutes))
							seen[s.Name] = true
						}
					}
				}
			}
			if len(suggestions) >= 5 {
				break
			}
		}
	}

	// Then: any station with name overlap (no route filter)
	if len(suggestions) < 5 {
		for _, s := range stations {
			norm := normalize(s.Name)
			queryWords := strings.Fields(query)
			for _, qw := range queryWords {
				if len(qw) >= 3 && strings.Contains(norm, qw) {
					if !seen[s.Name] {
						suggestions = append(suggestions, fmt.Sprintf("  %s (%s)", s.Name, s.DaytimeRoutes))
						seen[s.Name] = true
					}
				}
			}
			if len(suggestions) >= 5 {
				break
			}
		}
	}

	// If still nothing, just show some stations on this route
	if len(suggestions) == 0 && route != "" {
		count := 0
		for _, s := range stations {
			if containsRoute(s.Routes, route) && !seen[s.Name] {
				suggestions = append(suggestions, fmt.Sprintf("  %s (%s)", s.Name, s.DaytimeRoutes))
				seen[s.Name] = true
				count++
				if count >= 5 {
					break
				}
			}
		}
	}

	return suggestions
}

func formatSuggestions(suggestions []string) string {
	return strings.Join(suggestions, "\n")
}

// AllRoutes returns all known route IDs from the CSV.
func AllRoutes() []string {
	stations := loadStations()
	seen := make(map[string]bool)
	var routes []string
	for _, s := range stations {
		for _, r := range s.Routes {
			if !seen[r] {
				routes = append(routes, r)
				seen[r] = true
			}
		}
	}
	return routes
}

// IsValidRoute checks if a route ID is known.
func IsValidRoute(route string) bool {
	route = strings.ToUpper(strings.TrimSpace(route))
	for _, r := range AllRoutes() {
		if r == route {
			return true
		}
	}
	return false
}
