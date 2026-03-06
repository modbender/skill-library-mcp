
package cmd

import (
	"fmt"
	"os"
	"text/tabwriter"
	"strconv"
	"github.com/spf13/cobra"
)

// getCmd represents the get command
var getCmd = &cobra.Command{
	Use:   "get [RELEASE_ID]",
	Short: "Get detailed information for a single release in your collection",
	Long: `Fetches and displays detailed information for a specific release in your Discogs collection,
including tracklist, genre, year, and lowest marketplace price.`,
	Args: cobra.ExactArgs(1), // Requires exactly one argument: the release ID
	Run: func(cmd *cobra.Command, args []string) {
		releaseID, err := strconv.Atoi(args[0])
		if err != nil {
			fmt.Println("Error: Invalid Release ID. Please provide a number.")
			os.Exit(1)
		}

		client := newDiscogsClient()
		release, err := client.Release(releaseID)
		if err != nil {
			fmt.Printf("Error getting release details: %v\n", err)
			os.Exit(1)
		}

		w := new(tabwriter.Writer)
		w.Init(os.Stdout, 0, 8, 2, '\t', 0)

		if len(release.Artists) > 0 {
			fmt.Fprintf(w, "Artist:\t%s\n", release.Artists[0].Name)
		}
		fmt.Fprintf(w, "Title:\t%s\n", release.Title)
		fmt.Fprintf(w, "ID:\t%d\n", release.ID)
		fmt.Fprintf(w, "Year:\t%d\n", release.Year)
		if len(release.Genres) > 0 {
			fmt.Fprintf(w, "Genre:\t%s\n", release.Genres[0])
		}
		if release.LowestPrice > 0 {
			fmt.Fprintf(w, "Lowest Price:\t$%.2f\n", release.LowestPrice)
		}
		if len(release.Images) > 0 {
			fmt.Fprintf(w, "Album Art:\t%s\n", release.Images[0].URI)
		}

		fmt.Fprintln(w, "\n--- Tracklist ---")
		for _, track := range release.Tracklist {
			fmt.Fprintf(w, "%s\t%s\t%s\n", track.Position, track.Title, track.Duration)
		}

		w.Flush()
	},
}

func init() {
	collectionCmd.AddCommand(getCmd)
}
