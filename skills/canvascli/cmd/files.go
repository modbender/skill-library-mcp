package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"

	"canvas-cli/internal/ui"
)

func runFiles(args []string) {
	if len(args) == 0 {
		ui.Error("usage: canvas-cli files <course_id>")
		os.Exit(1)
	}

	courseID := args[0]

	data, err := client.GET(fmt.Sprintf("/courses/%s/files?sort=updated_at&order=desc", courseID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var files []struct {
		ID          int    `json:"id"`
		DisplayName string `json:"display_name"`
		Filename    string `json:"filename"`
		Size        int    `json:"size"`
		ContentType string `json:"content_type"`
		CreatedAt   string `json:"created_at"`
		UpdatedAt   string `json:"updated_at"`
		FolderID    int    `json:"folder_id"`
	}
	if err := json.Unmarshal(data, &files); err != nil {
		ui.Error("parsing files: " + err.Error())
		os.Exit(1)
	}

	ui.Header(fmt.Sprintf("Files — Course %s", courseID))

	rows := make([][]string, 0, len(files))
	for _, f := range files {
		size := formatSize(f.Size)
		rows = append(rows, []string{
			fmt.Sprintf("%d", f.ID),
			ui.Truncate(f.DisplayName, 40),
			size,
			f.ContentType,
			ui.FormatDate(f.UpdatedAt),
		})
	}

	ui.Table([]string{"ID", "NAME", "SIZE", "TYPE", "UPDATED"}, rows)
	fmt.Println()
}

func runDownload(args []string) {
	if len(args) == 0 {
		ui.Error("usage: canvas-cli download <file_id> [-o output_path]")
		os.Exit(1)
	}

	fileID := args[0]
	outputPath := ""

	for i := 1; i < len(args); i++ {
		if args[i] == "-o" && i+1 < len(args) {
			outputPath = args[i+1]
			i++
		}
	}

	// Get file metadata
	data, err := client.GET(fmt.Sprintf("/files/%s", fileID))
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	var file struct {
		ID          int    `json:"id"`
		DisplayName string `json:"display_name"`
		Filename    string `json:"filename"`
		URL         string `json:"url"`
		Size        int    `json:"size"`
	}
	if err := json.Unmarshal(data, &file); err != nil {
		ui.Error("parsing file info: " + err.Error())
		os.Exit(1)
	}

	if file.URL == "" {
		ui.Error("no download URL available for this file")
		os.Exit(1)
	}

	if outputPath == "" {
		outputPath = file.DisplayName
		if outputPath == "" {
			outputPath = file.Filename
		}
	}

	// Resolve to absolute path if relative
	if !filepath.IsAbs(outputPath) {
		cwd, _ := os.Getwd()
		outputPath = filepath.Join(cwd, outputPath)
	}

	ui.Info(fmt.Sprintf("Downloading %s (%s)...", file.DisplayName, formatSize(file.Size)))

	// Download the file
	resp, err := http.Get(file.URL)
	if err != nil {
		ui.Error("download failed: " + err.Error())
		os.Exit(1)
	}
	defer resp.Body.Close()

	out, err := os.Create(outputPath)
	if err != nil {
		ui.Error("creating file: " + err.Error())
		os.Exit(1)
	}
	defer out.Close()

	written, err := io.Copy(out, resp.Body)
	if err != nil {
		ui.Error("writing file: " + err.Error())
		os.Exit(1)
	}

	ui.Success(fmt.Sprintf("Downloaded %s (%s)", outputPath, formatSize(int(written))))
	fmt.Println()
}

func formatSize(bytes int) string {
	switch {
	case bytes >= 1024*1024*1024:
		return fmt.Sprintf("%.1f GB", float64(bytes)/(1024*1024*1024))
	case bytes >= 1024*1024:
		return fmt.Sprintf("%.1f MB", float64(bytes)/(1024*1024))
	case bytes >= 1024:
		return fmt.Sprintf("%.1f KB", float64(bytes)/1024)
	default:
		return fmt.Sprintf("%d B", bytes)
	}
}
