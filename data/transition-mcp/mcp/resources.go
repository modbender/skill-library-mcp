package main

import (
	"context"
	"fmt"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func registerResources(s *mcp.Server, client *TransitionClient) {
	// transition://athlete/profile
	s.AddResource(&mcp.Resource{
		URI:         "transition://athlete/profile",
		Name:        "Athlete Profile",
		Description: "Goals, experience level, training preferences, and equipment",
		MIMEType:    "application/json",
	}, func(ctx context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
		data, err := client.Get("/api/v1/profile")
		if err != nil {
			return nil, fmt.Errorf("failed to get profile: %w", err)
		}
		return &mcp.ReadResourceResult{
			Contents: []*mcp.ResourceContents{{
				URI:  "transition://athlete/profile",
				Text: data,
			}},
		}, nil
	})

	// transition://athlete/recent-activities
	s.AddResource(&mcp.Resource{
		URI:         "transition://athlete/recent-activities",
		Name:        "Recent Activities",
		Description: "Workouts and matched activities from the last 14 days",
		MIMEType:    "application/json",
	}, func(ctx context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
		end := time.Now().Format("2006-01-02")
		start := time.Now().AddDate(0, 0, -13).Format("2006-01-02")
		data, err := client.Get(fmt.Sprintf("/api/v1/workouts?start=%s&end=%s", start, end))
		if err != nil {
			return nil, fmt.Errorf("failed to get recent activities: %w", err)
		}
		return &mcp.ReadResourceResult{
			Contents: []*mcp.ResourceContents{{
				URI:  "transition://athlete/recent-activities",
				Text: data,
			}},
		}, nil
	})

	// transition://athlete/performance
	s.AddResource(&mcp.Resource{
		URI:         "transition://athlete/performance",
		Name:        "Performance Data",
		Description: "FTP, threshold paces, heart rate zones, and PMC (CTL/ATL/TSB) data",
		MIMEType:    "application/json",
	}, func(ctx context.Context, req *mcp.ReadResourceRequest) (*mcp.ReadResourceResult, error) {
		stats, err := client.Get("/api/v1/performance/stats")
		if err != nil {
			return nil, fmt.Errorf("failed to get performance stats: %w", err)
		}
		pmc, err := client.Get("/api/v1/performance/pmc")
		if err != nil {
			return nil, fmt.Errorf("failed to get PMC data: %w", err)
		}
		combined := fmt.Sprintf(`{"stats":%s,"pmc":%s}`, stats, pmc)
		return &mcp.ReadResourceResult{
			Contents: []*mcp.ResourceContents{{
				URI:  "transition://athlete/performance",
				Text: combined,
			}},
		}, nil
	})
}
