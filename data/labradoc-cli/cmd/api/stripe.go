package api

import (
	"bytes"
	"io"
	"os"
	"strings"

	"github.com/spf13/cobra"
)

var stripeCmd = &cobra.Command{
	Use:   "stripe",
	Short: "Stripe billing endpoints",
}

var stripeCheckoutCmd = &cobra.Command{
	Use:   "checkout",
	Short: "Create a Stripe checkout session for AI credit purchase",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simplePost(cmd, "/api/stripe/checkout", nil, "application/json", "")
	},
}

var stripePagesCheckoutCmd = &cobra.Command{
	Use:   "pages-checkout",
	Short: "Create a Stripe checkout session for the unlimited pages subscription",
	RunE: func(cmd *cobra.Command, _ []string) error {
		return simplePost(cmd, "/api/stripe/pages/checkout", nil, "application/json", "")
	},
}

var (
	stripeWebhookBody     string
	stripeWebhookBodyFile string
)

var stripeWebhookCmd = &cobra.Command{
	Use:   "webhook",
	Short: "Stripe webhook endpoint",
	RunE: func(cmd *cobra.Command, _ []string) error {
		body, err := readStripeBody()
		if err != nil {
			return err
		}
		return simplePostNoAuth(cmd, "/api/stripe/webhook", body, "application/json", "")
	},
}

func init() {
	stripeCmd.AddCommand(stripeCheckoutCmd)
	stripeCmd.AddCommand(stripePagesCheckoutCmd)
	stripeCmd.AddCommand(stripeWebhookCmd)

	stripeWebhookCmd.Flags().StringVar(&stripeWebhookBody, "body", "", "Request body as a string")
	stripeWebhookCmd.Flags().StringVar(&stripeWebhookBodyFile, "body-file", "", "Request body file ('-' for stdin)")
}

func readStripeBody() (io.Reader, error) {
	if stripeWebhookBodyFile != "" {
		if stripeWebhookBodyFile == "-" {
			return os.Stdin, nil
		}
		b, err := os.ReadFile(stripeWebhookBodyFile)
		if err != nil {
			return nil, err
		}
		return bytes.NewReader(b), nil
	}
	if strings.TrimSpace(stripeWebhookBody) != "" {
		return strings.NewReader(stripeWebhookBody), nil
	}
	return nil, nil
}
