package cmd

import (
	"errors"
	"fmt"

	"github.com/blanxlait/krocli/internal/config"
	"github.com/blanxlait/krocli/internal/krogerapi"
	"github.com/blanxlait/krocli/internal/outfmt"
	"github.com/blanxlait/krocli/internal/ui"
)

type ProductsCmd struct {
	Search ProductsSearchCmd `cmd:"" help:"Search for products."`
	Get    ProductsGetCmd    `cmd:"" help:"Get a product by ID."`
}

type ProductsSearchCmd struct {
	Term       string `required:"" help:"Search term." short:"t"`
	LocationID string `help:"Filter by location ID." short:"l"`
	Limit      int    `help:"Max results." default:"10"`
}

func (c *ProductsSearchCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.SearchProducts(c.Term, c.LocationID, c.Limit)
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	if flags.Plain {
		var rows [][]string
		for _, p := range resp.Data {
			rows = append(rows, []string{p.ProductID, p.Brand, p.Description})
		}
		outfmt.PrintPlain(rows)
		return nil
	}
	for _, p := range resp.Data {
		ui.Info("%s  %s — %s", p.ProductID, p.Brand, p.Description)
	}
	_, _ = fmt.Fprintf(fmtStderr, "%d results\n", len(resp.Data))
	return nil
}

type ProductsGetCmd struct {
	ID string `arg:"" help:"Product ID."`
}

func (c *ProductsGetCmd) Run(flags *RootFlags) error {
	creds, err := config.LoadCredentials()
	if err != nil && !errors.Is(err, config.ErrNoCredentials) {
		return err
	}
	client := krogerapi.NewClient(creds)
	resp, err := client.GetProduct(c.ID)
	if err != nil {
		return err
	}
	if flags.JSON {
		return outfmt.PrintJSON(resp)
	}
	for _, p := range resp.Data {
		ui.Info("%s  %s — %s", p.ProductID, p.Brand, p.Description)
	}
	return nil
}
