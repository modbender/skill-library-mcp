package cmd

import (
	"errors"

	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/krogerapi"
	"github.com/blanxlait/krocli/internal/outfmt"
	"github.com/blanxlait/krocli/internal/ui"
)

type IdentityCmd struct {
	Profile IdentityProfileCmd `cmd:"" help:"Get user profile."`
}

type IdentityProfileCmd struct{}

func (c *IdentityProfileCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.GetProfile()
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	ui.Info("Profile ID: %s", resp.Data.ID)
	return nil
}
