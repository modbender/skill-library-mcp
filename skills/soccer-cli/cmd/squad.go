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
	rootCmd.AddCommand(squadCmd)
}

var squadCmd = &cobra.Command{
	Use:   "squad [fixture-id]",
	Short: "Get the squad, ratings, and minutes played for a specific game.",
	Long:  `Retrieves and displays the starting lineup, player ratings, and minutes played for a given fixture ID.`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		fixtureID, err := strconv.Atoi(args[0])
		if err != nil {
			fmt.Println("Invalid fixture ID. It must be a number.")
			os.Exit(1)
		}

		client := api.NewClient(ApiKey)
		teamStats, err := client.GetPlayerStatsForFixture(fixtureID)
		if err != nil {
			fmt.Printf("Error fetching player stats: %v\n", err)
			os.Exit(1)
		}

		if len(teamStats) < 2 { // Expecting two teams
			fmt.Println("Could not retrieve full squad data for this match. The game may not have happened yet or data is unavailable.")
			os.Exit(0)
		}
		
		homeTeam := teamStats[0]
		awayTeam := teamStats[1]

		// --- Home Team Table ---
		fmt.Printf("\n--- %s ---\n", homeTeam.Team.Name)
		homeTable := tablewriter.NewWriter(os.Stdout)
		homeTable.SetHeader([]string{"Player", "Position", "Minutes", "Rating"})
		for _, playerDetail := range homeTeam.Players {
			stats := playerDetail.Statistics[0] // Assuming one set of stats per player per game
			if stats.Games.Minutes > 0 { 
				homeTable.Append([]string{
					playerDetail.Player.Name,
					stats.Games.Position,
					strconv.Itoa(stats.Games.Minutes),
					stats.Games.Rating,
				})
			}
		}
		homeTable.Render()

		// --- Away Team Table ---
		fmt.Printf("\n--- %s ---\n", awayTeam.Team.Name)
		awayTable := tablewriter.NewWriter(os.Stdout)
		awayTable.SetHeader([]string{"Player", "Position", "Minutes", "Rating"})
		for _, playerDetail := range awayTeam.Players {
			stats := playerDetail.Statistics[0]
			if stats.Games.Minutes > 0 {
				awayTable.Append([]string{
					playerDetail.Player.Name,
					stats.Games.Position,
					strconv.Itoa(stats.Games.Minutes),
					stats.Games.Rating,
				})
			}
		}
		awayTable.Render()
	},
}
