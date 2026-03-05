package cmd

import (
	"fmt"
	"os"
	"strconv"

	"github.com/jrojas537/soccer-cli/pkg/api"
	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(gameCmd)
}

var gameCmd = &cobra.Command{
	Use:   "game [fixture-id]",
	Short: "Get detailed events for a specific game.",
	Long:  `Retrieves and displays detailed events like goals, assists, and cards for a given fixture ID.`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		fixtureID, err := strconv.Atoi(args[0])
		if err != nil {
			fmt.Println("Invalid fixture ID. It must be a number.")
			os.Exit(1)
		}

		client := api.NewClient(ApiKey)
		details, err := client.GetFixtureDetails(fixtureID)
		if err != nil {
			fmt.Printf("Error fetching game details: %v\n", err)
			os.Exit(1)
		}

		if len(details) == 0 {
			fmt.Println("No game found with that ID.")
			os.Exit(0)
		}

		fixture := details[0]
		fmt.Printf("Match: %s vs %s (%s)\n", fixture.Teams.Home.Name, fixture.Teams.Away.Name, fixture.League.Name)
		fmt.Printf("Score: %d - %d\n\n", fixture.Goals.Home, fixture.Goals.Away)

		// --- Goals Table ---
		goalTable := tablewriter.NewWriter(os.Stdout)
		goalTable.SetHeader([]string{"Minute", "Team", "Scorer", "Assist"})
		goalTable.SetCaption(true, "Goals")

		// --- Cards Table ---
		cardTable := tablewriter.NewWriter(os.Stdout)
		cardTable.SetHeader([]string{"Minute", "Team", "Player", "Card"})
		cardTable.SetCaption(true, "Cards")

		for _, event := range fixture.Events {
			minute := strconv.Itoa(event.Time.Elapsed) + "'"
			if event.Type == "Goal" {
				goalTable.Append([]string{minute, event.Team.Name, event.Player.Name, event.Assist.Name})
			}
			if event.Type == "Card" {
				cardTable.Append([]string{minute, event.Team.Name, event.Player.Name, event.Detail})
			}
		}

		if goalTable.NumLines() > 0 {
			goalTable.Render()
			fmt.Println()
		} else {
			fmt.Println("No goals scored in this match.")
		}

		if cardTable.NumLines() > 0 {
			cardTable.Render()
		} else {
			fmt.Println("No cards issued in this match.")
		}
	},
}
