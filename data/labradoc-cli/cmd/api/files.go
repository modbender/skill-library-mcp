package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"strings"

	"github.com/zamedic/labradoc-cli/internal/cli"

	"github.com/spf13/cobra"
)

var filesCmd = &cobra.Command{
	Use:   "files",
	Short: "File operations via the API",
}

var (
	filesStatus     []string
	filesPageSize   int
	filesPageNumber int
)

var fileStatusOptions = []string{
	"New",
	"multipart",
	"googleDocument",
	"Check_Duplicate",
	"detectFileType",
	"htmlToPdf",
	"preview",
	"ocr",
	"process_image",
	"embedding",
	"name_predictor",
	"document_type",
	"extraction",
	"task",
	"completed",
	"ignored",
	"error",
	"not_supported",
	"on_hold",
	"duplicated",
}

var fileStatusSet = func() map[string]struct{} {
	set := make(map[string]struct{}, len(fileStatusOptions))
	for _, status := range fileStatusOptions {
		set[status] = struct{}{}
	}
	return set
}()

var filesListCmd = &cobra.Command{
	Use:   "list",
	Short: "List files",
	Long:  "Retrieves list of files.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		opts, err := resolveAPIConfig()
		if err != nil {
			return err
		}
		if opts.APIKey == "" && opts.Token == "" {
			return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
		}

		query := url.Values{}
		for _, s := range filesStatus {
			status := strings.TrimSpace(s)
			if status == "" {
				continue
			}
			if _, ok := fileStatusSet[status]; !ok {
				return fmt.Errorf("invalid status %q; valid values: %s", status, strings.Join(fileStatusOptions, ", "))
			}
			query.Add("status", status)
		}
		if filesPageSize > 0 {
			query.Set("pageSize", fmt.Sprintf("%d", filesPageSize))
		}
		if filesPageNumber > 0 {
			query.Set("pageNumber", fmt.Sprintf("%d", filesPageNumber))
		}
		path := "/api/user/files"
		if qs := query.Encode(); qs != "" {
			path = path + "?" + qs
		}

		resp, err := cli.DoRequest(cmd.Context(), "GET", path, nil, opts)
		if err != nil {
			return err
		}
		defer resp.Body.Close()
		if _, err := io.Copy(os.Stdout, resp.Body); err != nil {
			return err
		}
		if resp.StatusCode >= 400 {
			return fmt.Errorf("request failed: %s", resp.Status)
		}
		return nil
	},
}

var (
	uploadFilePath string
)

var filesUploadCmd = &cobra.Command{
	Use:   "upload",
	Short: "Upload files",
	Long:  "Uploads files.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if uploadFilePath == "" {
			return fmt.Errorf("missing --file")
		}
		opts, err := resolveAPIConfig()
		if err != nil {
			return err
		}
		if opts.APIKey == "" && opts.Token == "" {
			return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
		}

		f, err := os.Open(uploadFilePath)
		if err != nil {
			return err
		}
		defer f.Close()

		var body bytes.Buffer
		writer := multipart.NewWriter(&body)
		part, err := writer.CreateFormFile("file", filepath.Base(uploadFilePath))
		if err != nil {
			return err
		}
		if _, err := io.Copy(part, f); err != nil {
			return err
		}
		if err := writer.Close(); err != nil {
			return err
		}

		opts.Headers = map[string]string{
			"Content-Type": writer.FormDataContentType(),
		}
		resp, err := cli.DoRequest(cmd.Context(), "PUT", "/api/user/files", &body, opts)
		if err != nil {
			return err
		}
		defer resp.Body.Close()
		if _, err := io.Copy(os.Stdout, resp.Body); err != nil {
			return err
		}
		if resp.StatusCode >= 400 {
			return fmt.Errorf("request failed: %s", resp.Status)
		}
		return nil
	},
}

var (
	fileID       string
	filesOutPath string
)

var filesGetCmd = &cobra.Command{
	Use:   "get",
	Short: "Get file",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s", fileID), "")
	},
}

var filesContentCmd = &cobra.Command{
	Use:   "content",
	Short: "Get file content",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/content", fileID), filesOutPath)
	},
}

var filesOcrCmd = &cobra.Command{
	Use:   "ocr",
	Short: "Get OCR content for document",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/ocr", fileID), filesOutPath)
	},
}

var filesDownloadCmd = &cobra.Command{
	Use:   "download",
	Short: "Download file",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		out := filesOutPath
		if out == "" {
			out = fileID + ".pdf"
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/download", fileID), out)
	},
}

var (
	questionText string
	bodyText     string
	bodyFile     string
)

var filesQuestionCmd = &cobra.Command{
	Use:   "question",
	Short: "Ask question about file",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		body, err := readJSONBody()
		if err != nil {
			return err
		}
		if body == nil {
			return fmt.Errorf("missing request body (--question, --body, or --body-file)")
		}
		return simplePost(cmd, fmt.Sprintf("/api/user/files/%s/question", fileID), body, "application/json", filesOutPath)
	},
}

var filesSearchCmd = &cobra.Command{
	Use:   "search",
	Short: "Search files using agent",
	Long:  "Searches files using an AI agent. Returns a streaming response using Server-Sent Events (SSE) that provides real-time feedback as the agent processes the request.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		body, err := readJSONBody()
		if err != nil {
			return err
		}
		if body == nil {
			return fmt.Errorf("missing request body (--question, --body, or --body-file)")
		}
		return simplePost(cmd, "/api/user/files", body, "application/json", filesOutPath)
	},
}

var (
	archiveID  string
	archiveIDs []string
)

var filesArchiveCmd = &cobra.Command{
	Use:   "archive",
	Short: "Archive files",
	Long:  "Archives files by IDs; archived files are excluded from retrieval.",
	RunE: func(cmd *cobra.Command, _ []string) error {
		ids := make([]string, 0, len(archiveIDs))
		if archiveID != "" {
			ids = append(ids, archiveID)
		}
		for _, id := range archiveIDs {
			if strings.TrimSpace(id) != "" {
				ids = append(ids, strings.TrimSpace(id))
			}
		}
		if len(ids) == 0 {
			return fmt.Errorf("missing --id or --ids")
		}
		body, err := json.Marshal(map[string]any{"ids": ids})
		if err != nil {
			return err
		}
		return simplePost(cmd, "/api/user/files/archive", bytes.NewReader(body), "application/json", filesOutPath)
	},
}

var filesFieldsCmd = &cobra.Command{
	Use:   "fields",
	Short: "Get extracted fields",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/fields", fileID), filesOutPath)
	},
}

var filesRelatedCmd = &cobra.Command{
	Use:   "related",
	Short: "Get related documents",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/related", fileID), filesOutPath)
	},
}

var filesReprocessCmd = &cobra.Command{
	Use:   "reprocess",
	Short: "Reprocess file",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/reprocess", fileID), filesOutPath)
	},
}

var filesTasksCmd = &cobra.Command{
	Use:   "tasks",
	Short: "Get tasks for document",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/tasks", fileID), filesOutPath)
	},
}

var (
	imagePageNumber int
)

var filesImageCmd = &cobra.Command{
	Use:   "image",
	Short: "Get file page image",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		if imagePageNumber <= 0 {
			return fmt.Errorf("missing or invalid --page")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/image/%d", fileID, imagePageNumber), filesOutPath)
	},
}

var filesPreviewCmd = &cobra.Command{
	Use:   "preview",
	Short: "Get a smaller preview image of the file",
	RunE: func(cmd *cobra.Command, _ []string) error {
		if fileID == "" {
			return fmt.Errorf("missing --id")
		}
		if imagePageNumber <= 0 {
			return fmt.Errorf("missing or invalid --page")
		}
		return simpleGet(cmd, fmt.Sprintf("/api/user/files/%s/image/preview/%d", fileID, imagePageNumber), filesOutPath)
	},
}

func init() {
	filesCmd.AddCommand(filesListCmd)
	filesCmd.AddCommand(filesUploadCmd)
	filesCmd.AddCommand(filesGetCmd)
	filesCmd.AddCommand(filesContentCmd)
	filesCmd.AddCommand(filesOcrCmd)
	filesCmd.AddCommand(filesDownloadCmd)
	filesCmd.AddCommand(filesQuestionCmd)
	filesCmd.AddCommand(filesSearchCmd)
	filesCmd.AddCommand(filesArchiveCmd)
	filesCmd.AddCommand(filesFieldsCmd)
	filesCmd.AddCommand(filesRelatedCmd)
	filesCmd.AddCommand(filesReprocessCmd)
	filesCmd.AddCommand(filesTasksCmd)
	filesCmd.AddCommand(filesImageCmd)
	filesCmd.AddCommand(filesPreviewCmd)

	filesListCmd.Flags().StringSliceVar(&filesStatus, "status", nil, "Filter by status (repeatable). Valid values: "+strings.Join(fileStatusOptions, ", "))
	filesListCmd.Flags().IntVar(&filesPageSize, "page-size", 0, "Page size")
	filesListCmd.Flags().IntVar(&filesPageNumber, "page-number", 0, "Page number")

	filesUploadCmd.Flags().StringVar(&uploadFilePath, "file", "", "Path to the file to upload")

	filesGetCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesContentCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesOcrCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesDownloadCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesQuestionCmd.Flags().StringVar(&fileID, "id", "", "File ID")

	filesContentCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesOcrCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesDownloadCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesQuestionCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesSearchCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesArchiveCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesFieldsCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesRelatedCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesReprocessCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesTasksCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesImageCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")
	filesPreviewCmd.Flags().StringVar(&filesOutPath, "out", "", "Write response to file instead of stdout")

	filesQuestionCmd.Flags().StringVar(&questionText, "question", "", "Question text (JSON field: question)")
	filesQuestionCmd.Flags().StringVar(&bodyText, "body", "", "Request body as a JSON string")
	filesQuestionCmd.Flags().StringVar(&bodyFile, "body-file", "", "Request body JSON file ('-' for stdin)")
	filesSearchCmd.Flags().StringVar(&questionText, "question", "", "Question text (JSON field: question)")
	filesSearchCmd.Flags().StringVar(&bodyText, "body", "", "Request body as a JSON string")
	filesSearchCmd.Flags().StringVar(&bodyFile, "body-file", "", "Request body JSON file ('-' for stdin)")

	filesArchiveCmd.Flags().StringVar(&archiveID, "id", "", "File ID to archive")
	filesArchiveCmd.Flags().StringSliceVar(&archiveIDs, "ids", nil, "File IDs to archive (repeatable)")

	filesFieldsCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesRelatedCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesReprocessCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesTasksCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesImageCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesPreviewCmd.Flags().StringVar(&fileID, "id", "", "File ID")
	filesImageCmd.Flags().IntVar(&imagePageNumber, "page", 0, "Page number")
	filesPreviewCmd.Flags().IntVar(&imagePageNumber, "page", 0, "Page number")
}

func readJSONBody() (io.Reader, error) {
	if bodyFile != "" {
		if bodyFile == "-" {
			return os.Stdin, nil
		}
		b, err := os.ReadFile(bodyFile)
		if err != nil {
			return nil, err
		}
		return bytes.NewReader(b), nil
	}
	if bodyText != "" {
		return strings.NewReader(bodyText), nil
	}
	if questionText != "" {
		payload := map[string]string{"question": questionText}
		b, err := json.Marshal(payload)
		if err != nil {
			return nil, err
		}
		return bytes.NewReader(b), nil
	}
	return nil, nil
}

func simpleGet(cmd *cobra.Command, path string, outPath string) error {
	opts, err := resolveAPIConfig()
	if err != nil {
		return err
	}
	if opts.APIKey == "" && opts.Token == "" {
		return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
	}
	resp, err := cli.DoRequest(cmd.Context(), "GET", path, nil, opts)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return writeResponse(resp, outPath)
}

func simplePost(cmd *cobra.Command, path string, body io.Reader, contentType string, outPath string) error {
	opts, err := resolveAPIConfig()
	if err != nil {
		return err
	}
	if opts.APIKey == "" && opts.Token == "" {
		return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
	}
	opts.Headers = map[string]string{
		"Content-Type": contentType,
	}
	resp, err := cli.DoRequest(cmd.Context(), "POST", path, body, opts)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return writeResponse(resp, outPath)
}

func simplePostNoAuth(cmd *cobra.Command, path string, body io.Reader, contentType string, outPath string) error {
	opts, err := resolveAPIConfig()
	if err != nil {
		return err
	}
	opts.Headers = map[string]string{
		"Content-Type": contentType,
	}
	resp, err := cli.DoRequest(cmd.Context(), "POST", path, body, opts)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return writeResponse(resp, outPath)
}

func simpleDelete(cmd *cobra.Command, path string, outPath string) error {
	opts, err := resolveAPIConfig()
	if err != nil {
		return err
	}
	if opts.APIKey == "" && opts.Token == "" {
		return fmt.Errorf("missing api token (use --api-token, --token, api_token, or --use-auth-token)")
	}
	resp, err := cli.DoRequest(cmd.Context(), "DELETE", path, nil, opts)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return writeResponse(resp, outPath)
}

func writeResponse(resp *http.Response, outPath string) error {
	var out io.Writer = os.Stdout
	if outPath != "" {
		f, err := os.Create(outPath)
		if err != nil {
			return err
		}
		defer f.Close()
		out = f
	}
	if _, err := io.Copy(out, resp.Body); err != nil {
		return err
	}
	if resp.StatusCode >= 400 {
		return fmt.Errorf("request failed: %s", resp.Status)
	}
	return nil
}
