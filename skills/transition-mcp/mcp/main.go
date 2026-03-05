package main

import (
	"context"
	"log"
	"os"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func main() {
	apiKey := os.Getenv("TRANSITION_API_KEY")
	baseURL := os.Getenv("TRANSITION_API_URL")
	if baseURL == "" {
		baseURL = "https://api.transition.fun"
	}

	client := NewTransitionClient(baseURL, apiKey)

	server := mcp.NewServer(&mcp.Implementation{
		Name:    "transition-mcp",
		Version: "1.0.0",
	}, nil)

	registerTools(server, client)
	registerResources(server, client)

	if err := server.Run(context.Background(), &mcp.StdioTransport{}); err != nil {
		log.Fatal(err)
	}
}
