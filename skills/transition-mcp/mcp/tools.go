package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

// parseArgs unmarshals the raw JSON arguments into a map
func parseArgs(raw json.RawMessage) map[string]interface{} {
	var args map[string]interface{}
	if len(raw) > 0 {
		json.Unmarshal(raw, &args)
	}
	if args == nil {
		args = map[string]interface{}{}
	}
	return args
}

func registerTools(s *mcp.Server, client *TransitionClient) {
	// get_todays_workout - Get today's scheduled workout
	s.AddTool(&mcp.Tool{
		Name:        "get_todays_workout",
		Description: "Get today's scheduled workout from your training plan",
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		today := time.Now().Format("2006-01-02")
		data, err := client.Get(fmt.Sprintf("/api/v1/workouts?start=%s&end=%s", today, today))
		if err != nil {
			return errorResult(fmt.Sprintf("Failed to get today's workout: %v", err)), nil
		}
		return textResult(data), nil
	})

	// get_week_plan - Get 7-day training plan
	s.AddTool(&mcp.Tool{
		Name:        "get_week_plan",
		Description: "Get your training plan for the next 7 days",
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		start := time.Now().Format("2006-01-02")
		end := time.Now().AddDate(0, 0, 6).Format("2006-01-02")
		data, err := client.Get(fmt.Sprintf("/api/v1/workouts?start=%s&end=%s", start, end))
		if err != nil {
			return errorResult(fmt.Sprintf("Failed to get week plan: %v", err)), nil
		}
		return textResult(data), nil
	})

	// adapt_plan - Trigger plan adaptation
	s.AddTool(&mcp.Tool{
		Name:        "adapt_plan",
		Description: "Adapt your training plan based on recent performance, fatigue, or schedule changes. Use sparingly — only when the athlete explicitly wants plan changes.",
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args := parseArgs(req.Params.Arguments)
		body := map[string]interface{}{}
		if reason, ok := args["reason"].(string); ok {
			body["reason"] = reason
		}
		data, err := client.Post("/api/v1/workouts/adapt", body)
		if err != nil {
			return errorResult(fmt.Sprintf("Failed to adapt plan: %v", err)), nil
		}
		return textResult(data), nil
	})

	// get_fitness_metrics - Get CTL/ATL/TSB data
	s.AddTool(&mcp.Tool{
		Name:        "get_fitness_metrics",
		Description: "Get Performance Management Chart (PMC) data: CTL (fitness), ATL (fatigue), TSB (form). Check this before recommending hard workouts — if TSB is very negative, the athlete may need rest.",
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		data, err := client.Get("/api/v1/performance/pmc")
		if err != nil {
			return errorResult(fmt.Sprintf("Failed to get fitness metrics: %v", err)), nil
		}
		return textResult(data), nil
	})

	// chat_with_coach - AI coaching conversation
	s.AddTool(&mcp.Tool{
		Name:        "chat_with_coach",
		Description: "Chat with the AI endurance coach. Useful for training advice, workout explanations, race strategy, and nutrition guidance.",
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args := parseArgs(req.Params.Arguments)
		message, ok := args["message"].(string)
		if !ok || message == "" {
			return errorResult("message is required"), nil
		}
		body := map[string]interface{}{
			"message": message,
		}
		data, err := client.PostSSE("/api/v1/coach/chat", body)
		if err != nil {
			return errorResult(fmt.Sprintf("Failed to chat with coach: %v", err)), nil
		}
		return textResult(data), nil
	})

	// generate_workout - Free WOD (no auth needed)
	s.AddTool(&mcp.Tool{
		Name:        "generate_workout",
		Description: "Generate a Workout of the Day. Free, no API key needed. Good for quick standalone workouts.",
	}, func(ctx context.Context, req *mcp.CallToolRequest) (*mcp.CallToolResult, error) {
		args := parseArgs(req.Params.Arguments)
		sport := "run"
		duration := 45

		if s, ok := args["sport"].(string); ok {
			sport = s
		}
		if d, ok := args["duration"].(float64); ok {
			duration = int(d)
		}

		data, err := client.Get(fmt.Sprintf("/api/v1/wod?sport=%s&duration=%d", sport, duration))
		if err != nil {
			return errorResult(fmt.Sprintf("Failed to generate workout: %v", err)), nil
		}
		return textResult(data), nil
	})
}

func textResult(text string) *mcp.CallToolResult {
	return &mcp.CallToolResult{
		Content: []mcp.Content{
			&mcp.TextContent{Text: text},
		},
	}
}

func errorResult(msg string) *mcp.CallToolResult {
	return &mcp.CallToolResult{
		Content: []mcp.Content{
			&mcp.TextContent{Text: msg},
		},
		IsError: true,
	}
}
