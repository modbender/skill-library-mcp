package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strconv"

	"github.com/spf13/cobra"
)

var artCmd = &cobra.Command{
	Use:   "art [release_id]",
	Short: "Fetches the album art for a given release ID.",
	Long:  `Fetches and displays the primary album art for a specific Discogs release ID. The image will be sent to the chat.`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		releaseID, err := strconv.Atoi(args[0])
		if err != nil {
			fmt.Println("Error: Invalid Release ID. Must be a number.")
			return
		}

		client := &http.Client{}
		url := fmt.Sprintf("https://api.discogs.com/releases/%d", releaseID)
		req, err := http.NewRequest("GET", url, nil)
		if err != nil {
			fmt.Println("Error creating request:", err)
			return
		}

		// Discogs API requires a User-Agent header
		req.Header.Set("User-Agent", "OpenClawDiscogsCLI/1.2.0")

		resp, err := client.Do(req)
		if err != nil {
			fmt.Println("Error fetching release data:", err)
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode != http.StatusOK {
			fmt.Printf("Error: Received non-200 status code: %d %s\n", resp.StatusCode, resp.Status)
			return
		}

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			fmt.Println("Error reading response body:", err)
			return
		}

		var release Release
		if err := json.Unmarshal(body, &release); err != nil {
			fmt.Println("Error parsing JSON:", err)
			return
		}

		if len(release.Images) == 0 {
			fmt.Println("No images found for this release.")
			return
		}

		primaryImageURL := ""
		for _, img := range release.Images {
			if img.Type == "primary" {
				primaryImageURL = img.ResourceURL
				break
			}
		}

		if primaryImageURL == "" {
			// Fallback to the first image if no primary is found
			primaryImageURL = release.Images[0].ResourceURL
		}
		
		imageResp, err := http.Get(primaryImageURL)
		if err != nil {
			fmt.Println("Error downloading image:", err)
			return
		}
		defer imageResp.Body.Close()

		if imageResp.StatusCode != http.StatusOK {
			fmt.Println("Error: Failed to download image with status:", imageResp.Status)
			return
		}
		
		// Define the cache directory path within the OpenClaw workspace
		cacheDir := "/home/Ev05bot/.openclaw/workspace/art_cache/discogs"
		
		// Create the directory including any necessary parents
		if err := os.MkdirAll(cacheDir, os.ModePerm); err != nil {
			fmt.Println("Error creating cache directory:", err)
			return
		}

		// Save the image to the cache
		fileName := fmt.Sprintf("%d.jpg", releaseID)
		filePath := filepath.Join(cacheDir, fileName)

		file, err := os.Create(filePath)
		if err != nil {
			fmt.Println("Error creating file:", err)
			return
		}
		defer file.Close()

		_, err = io.Copy(file, imageResp.Body)
		if err != nil {
			fmt.Println("Error saving image:", err)
			return
		}
		
		// Print artist and title
		artistName := "Unknown Artist"
		if len(release.Artists) > 0 {
			artistName = release.Artists[0].Name
		}
		fmt.Printf("%s - %s\n", artistName, release.Title)

		// Output the MEDIA line for OpenClaw
		fmt.Printf("MEDIA: %s\n", filePath)
	},
}

func init() {
	releaseCmd.AddCommand(artCmd)
}
