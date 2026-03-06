package cmd

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/jrojas537/soccer-cli/pkg/api"
	"github.com/olekukonko/tablewriter"
	"github.com/spf13/cobra"
)

func init() {
	rootCmd.AddCommand(scoresCmd)
}

var scoresCmd = &cobra.Command{
	Use:   "scores [team-name]",
	Short: "Get the latest score for a specific team.",
	Long:  `Retrieves and displays the most recent match result for a given football team.`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		teamName := args[0]
		client := api.NewClient(ApiKey)

		teams, err := client.GetTeam(teamName)
		if err != nil {
			fmt.Printf("Error fetching team: %v\n", err)
			os.Exit(1)
		}

		if len(teams) == 0 {
			fmt.Printf("No team found matching '%s'\n", teamName)
			os.Exit(1)
		}
		
		// For simplicity, we'll use the first match
		teamID := teams[0].Team.ID
		fixtures, err := client.GetLatestFixturesForTeam(teamID, 1)
		if err != nil {
			fmt.Printf("Error fetching fixtures: %v\n", err)
			os.Exit(1)
		}

		if len(fixtures) == 0 {
			fmt.Println("No recent fixtures found for this team.")
			os.Exit(0)
		}

		fixture := fixtures[0]

		table := tablewriter.NewWriter(os.Stdout)
		table.SetHeader([]string{"ID", "Date", "Home", "Score", "Away", "Status"})
		
		score := fmt.Sprintf("%d - %d", fixture.Goals.Home, fixture.Goals.Away)
		date := time.Unix(int64(fixture.Fixture.Timestamp), 0).Format("2006-01-02")

		table.Append([]string{
			strconv.Itoa(fixture.Fixture.ID),
			date,
			fixture.Teams.Home.Name,
			score,
			fixture.Teams.Away.Name,
			fixture.Fixture.Status.Long,
		})
		
		table.Render()
	},
}
