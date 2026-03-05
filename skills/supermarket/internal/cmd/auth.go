package cmd

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"runtime"
	"strings"

	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/krogerapi"
	"github.com/blanxlait/krocli/internal/telegram"
	"github.com/blanxlait/krocli/internal/ui"
)

type AuthCmd struct {
	Login       AuthLoginCmd       `cmd:"" help:"Login via browser OAuth flow."`
	Status      AuthStatusCmd      `cmd:"" help:"Show current auth state."`
	Credentials AuthCredentialsCmd `cmd:"" help:"Manage API credentials."`
}

type AuthLoginCmd struct {
	SendLinkTelegram bool `name:"send-link-telegram" help:"Send OAuth login URL via Telegram instead of opening a browser."`
}

func (c *AuthLoginCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}

	openURL := openBrowser
	if c.SendLinkTelegram {
		openURL = sendViaTelegram
	}

	// creds is nil in hosted mode
	return krogerapi.LoginFlow(creds, openURL)
}

// stdinReader is used for prompting; tests replace this.
var stdinReader = func() *bufio.Reader { return bufio.NewReader(os.Stdin) }

func sendViaTelegram(loginURL string) error {
	cfg := config.OpenClawIntegration()
	if cfg == nil {
		var err error
		cfg, err = config.LoadTelegramConfig()
		if err != nil {
			if !errors.Is(err, config.ErrNoTelegramConfig) {
				return fmt.Errorf("load telegram config: %w", err)
			}
			cfg, err = promptAndSaveTelegramConfig()
			if err != nil {
				return fmt.Errorf("telegram configuration: %w", err)
			}
		}
	}

	msg := fmt.Sprintf("Kroger login URL:\n%s", loginURL)
	if err := telegram.SendMessage(cfg.BotToken, cfg.ChatID, msg); err != nil {
		return fmt.Errorf("send telegram message: %w", err)
	}
	ui.Success("Login URL sent via Telegram.")
	return nil
}

func promptAndSaveTelegramConfig() (*config.TelegramConfig, error) {
	reader := stdinReader()

	fmt.Fprint(os.Stderr, "Telegram bot token: ")
	botToken, err := reader.ReadString('\n')
	if err != nil {
		return nil, fmt.Errorf("read bot token: %w", err)
	}
	botToken = strings.TrimSpace(botToken)

	fmt.Fprint(os.Stderr, "Telegram chat ID: ")
	chatID, err := reader.ReadString('\n')
	if err != nil {
		return nil, fmt.Errorf("read chat ID: %w", err)
	}
	chatID = strings.TrimSpace(chatID)

	if botToken == "" || chatID == "" {
		return nil, fmt.Errorf("bot token and chat ID are required")
	}

	cfg := &config.TelegramConfig{BotToken: botToken, ChatID: chatID}
	if err := config.SaveTelegramConfig(cfg); err != nil {
		return nil, fmt.Errorf("save telegram config: %w", err)
	}
	ui.Success("Telegram config saved.")
	return cfg, nil
}

type AuthStatusCmd struct{}

func (c *AuthStatusCmd) Run(flags *RootFlags) error {
	if config.IsHostedMode() {
		ui.Info("Mode: hosted")
	} else {
		ui.Info("Mode: local")
	}
	clientOK, userOK := krogerapi.AuthStatus()
	if clientOK {
		ui.Success("Client token: valid")
	} else {
		ui.Warn("Client token: not available")
	}
	if userOK {
		ui.Success("User token: valid")
	} else {
		ui.Warn("User token: not available (run: krocli auth login)")
	}
	return nil
}

type AuthCredentialsCmd struct {
	Set AuthCredentialsSetCmd `cmd:"" help:"Import credentials from a JSON file."`
}

type AuthCredentialsSetCmd struct {
	Path string `arg:"" help:"Path to JSON file with client_id and client_secret."`
}

func (c *AuthCredentialsSetCmd) Run(flags *RootFlags) error {
	data, err := os.ReadFile(c.Path)
	if err != nil {
		return err
	}
	var creds config.Credentials
	if err := json.Unmarshal(data, &creds); err != nil {
		return err
	}
	if creds.ClientID == "" || creds.ClientSecret == "" {
		return errMissingCreds
	}
	if err := config.SaveCredentials(&creds); err != nil {
		return err
	}
	ui.Success("Credentials saved.")
	return nil
}

var errMissingCreds = errString("JSON must contain client_id and client_secret")

type errString string

func (e errString) Error() string { return string(e) }

func openBrowser(url string) error {
	switch runtime.GOOS {
	case "darwin":
		return exec.Command("open", url).Start()
	case "linux":
		return exec.Command("xdg-open", url).Start()
	default:
		return exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	}
}
