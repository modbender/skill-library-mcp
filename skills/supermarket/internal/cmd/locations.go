package cmd

import (
	"errors"
	"fmt"

	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/krogerapi"
	"github.com/blanxlait/krocli/internal/outfmt"
	"github.com/blanxlait/krocli/internal/ui"
)

type LocationsCmd struct {
	Search      LocationsSearchCmd `cmd:"" help:"Search for locations."`
	Get         LocationsGetCmd    `cmd:"" help:"Get a location by ID."`
	Chains      LocationsChainsCmd `cmd:"" help:"List store chains."`
	Departments LocationsDeptCmd   `cmd:"" help:"List departments."`
}

type LocationsSearchCmd struct {
	ZipCode string `required:"" help:"Zip code to search near." short:"z"`
	Radius  int    `help:"Radius in miles." default:"10"`
	Limit   int    `help:"Max results." default:"10"`
}

func (c *LocationsSearchCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.SearchLocations(c.ZipCode, c.Radius, c.Limit)
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	if flags.Plain {
		var rows [][]string
		for _, l := range resp.Data {
			rows = append(rows, []string{l.LocationID, l.Name, l.Address.City, l.Address.State})
		}
		outfmt.PrintPlain(rows)
		return nil
	}
	for _, l := range resp.Data {
		ui.Info("%s  %s — %s, %s %s", l.LocationID, l.Name, l.Address.AddressLine1, l.Address.City, l.Address.State)
	}
	_, _ = fmt.Fprintf(fmtStderr, "%d results\n", len(resp.Data))
	return nil
}

type LocationsGetCmd struct {
	ID string `arg:"" help:"Location ID."`
}

func (c *LocationsGetCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.GetLocation(c.ID)
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	for _, l := range resp.Data {
		ui.Info("%s  %s — %s, %s %s", l.LocationID, l.Name, l.Address.AddressLine1, l.Address.City, l.Address.State)
	}
	return nil
}

type LocationsChainsCmd struct{}

func (c *LocationsChainsCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.GetChains()
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	for _, ch := range resp.Data {
		ui.Info("%s", ch.Name)
	}
	return nil
}

type LocationsDeptCmd struct{}

func (c *LocationsDeptCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.GetDepartments()
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	for _, d := range resp.Data {
		ui.Info("%s  %s", d.DepartmentID, d.Name)
	}
	return nil
}
