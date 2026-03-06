package telegram

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
)

// HTTPClient is the HTTP client used for Telegram API requests. Tests override this.
var HTTPClient = http.DefaultClient

// BaseURL is the Telegram Bot API base URL. Tests override this.
var BaseURL = "https://api.telegram.org"

// SendMessage sends text to a Telegram chat via the Bot API.
func SendMessage(botToken, chatID, text string) error {
	if botToken == "" {
		return fmt.Errorf("telegram: bot token is required")
	}
	if chatID == "" {
		return fmt.Errorf("telegram: chat ID is required")
	}

	apiURL := fmt.Sprintf("%s/bot%s/sendMessage", BaseURL, botToken)
	params := url.Values{
		"chat_id": {chatID},
		"text":    {text},
	}

	resp, err := HTTPClient.PostForm(apiURL, params)
	if err != nil {
		return fmt.Errorf("telegram request: %w", err)
	}
	defer func() { _ = resp.Body.Close() }()

	body, _ := io.ReadAll(resp.Body)
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("telegram API %d: %s", resp.StatusCode, string(body))
	}

	var result struct {
		OK          bool   `json:"ok"`
		Description string `json:"description"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return fmt.Errorf("telegram response parse: %w", err)
	}
	if !result.OK {
		return fmt.Errorf("telegram API error: %s", result.Description)
	}
	return nil
}
