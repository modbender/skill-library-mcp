package cmd

import (
	"encoding/json"
	"fmt"
	"os"

	"canvas-cli/internal/ui"
)

func runWhoami() {
	data, err := client.GET("/users/self/profile")
	if err != nil {
		ui.Error(err.Error())
		os.Exit(1)
	}

	if jsonOutput {
		fmt.Println(string(data))
		return
	}

	var profile struct {
		ID        int    `json:"id"`
		Name      string `json:"name"`
		ShortName string `json:"short_name"`
		Email     string `json:"primary_email"`
		LoginID   string `json:"login_id"`
		Bio       string `json:"bio"`
		AvatarURL string `json:"avatar_url"`
		Locale    string `json:"locale"`
		TimeZone  string `json:"time_zone"`
	}
	if err := json.Unmarshal(data, &profile); err != nil {
		ui.Error("parsing profile: " + err.Error())
		os.Exit(1)
	}

	ui.Header("Your Profile")
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Name:"), profile.Name)
	fmt.Printf("  %s  %d\n", ui.C(ui.Bold, "ID:"), profile.ID)
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Email:"), profile.Email)
	fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Login:"), profile.LoginID)
	if profile.Bio != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "Bio:"), profile.Bio)
	}
	if profile.TimeZone != "" {
		fmt.Printf("  %s  %s\n", ui.C(ui.Bold, "TZ:"), profile.TimeZone)
	}
	fmt.Println()
}
