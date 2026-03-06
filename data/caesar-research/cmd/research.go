package cmd

import (
	"fmt"
	"io"
	"time"

	"github.com/alexrudloff/caesar-cli/internal/client"
	"github.com/alexrudloff/caesar-cli/internal/output"
	"github.com/spf13/cobra"
)

// pollInterval controls how often pollResearch polls. Tests can set this to 0.
var pollInterval = 3 * time.Second

func init() {
	rootCmd.AddCommand(researchCmd)
	researchCmd.AddCommand(researchCreateCmd)
	researchCmd.AddCommand(researchGetCmd)
	researchCmd.AddCommand(researchEventsCmd)
	researchCmd.AddCommand(researchWatchCmd)

	researchCreateCmd.Flags().Int("loops", 1, "Maximum reasoning loops")
	researchCreateCmd.Flags().Bool("reasoning", false, "Enable reasoning mode")
	researchCreateCmd.Flags().Bool("auto", false, "Auto-configure based on query")
	researchCreateCmd.Flags().Bool("exclude-social", false, "Exclude social media sources")
	researchCreateCmd.Flags().String("model", "", "Model to use (gpt-5.2, gemini-3-pro, gemini-3-flash, claude-opus-4.5)")
	researchCreateCmd.Flags().String("system-prompt", "", "Custom system prompt")
	researchCreateCmd.Flags().StringSlice("exclude-domain", nil, "Domains to exclude")
	researchCreateCmd.Flags().String("brainstorm", "", "Brainstorm session ID to use")
	researchCreateCmd.Flags().Bool("no-wait", false, "Return immediately without waiting for completion")
}

var researchCmd = &cobra.Command{
	Use:   "research",
	Short: "Manage research jobs",
}

var researchCreateCmd = &cobra.Command{
	Use:   "create [query]",
	Short: "Create a new research job",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		req := &client.CreateResearchRequest{Query: args[0]}
		req.ReasoningLoops, _ = cmd.Flags().GetInt("loops")
		req.ReasoningMode, _ = cmd.Flags().GetBool("reasoning")
		req.Auto, _ = cmd.Flags().GetBool("auto")
		req.ExcludeSocial, _ = cmd.Flags().GetBool("exclude-social")
		req.Model, _ = cmd.Flags().GetString("model")
		req.SystemPrompt, _ = cmd.Flags().GetString("system-prompt")
		req.ExcludedDomains, _ = cmd.Flags().GetStringSlice("exclude-domain")
		req.BrainstormSessionID, _ = cmd.Flags().GetString("brainstorm")

		resp, err := c.CreateResearch(req)
		if err != nil {
			output.Error("%v", err)
		}

		noWait, _ := cmd.Flags().GetBool("no-wait")
		if noWait {
			output.JSON(resp)
			return
		}

		result, err := pollResearch(c, cmd.OutOrStdout(), resp.ID)
		if err != nil {
			output.Error("%v", err)
		}
		output.JSON(result)
	},
}

var researchGetCmd = &cobra.Command{
	Use:   "get [id]",
	Short: "Get a research job by ID",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		res, err := c.GetResearch(args[0])
		if err != nil {
			output.Error("%v", err)
		}

		output.JSON(res)
	},
}

var researchEventsCmd = &cobra.Command{
	Use:   "events [id]",
	Short: "Get events for a research job",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		events, err := c.GetResearchEvents(args[0])
		if err != nil {
			output.Error("%v", err)
		}

		output.JSON(events)
	},
}

var researchWatchCmd = &cobra.Command{
	Use:   "watch [id]",
	Short: "Poll a research job until completion, printing events",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		result, err := pollResearch(c, cmd.OutOrStdout(), args[0])
		if err != nil {
			output.Error("%v", err)
		}

		output.JSON(result)
	},
}

func pollResearch(c *client.Client, w io.Writer, id string) (*client.ResearchObject, error) {
	seenEvents := 0
	for {
		res, err := c.GetResearch(id)
		if err != nil {
			return nil, err
		}

		events, err := c.GetResearchEvents(id)
		if err == nil && len(events) > seenEvents {
			for _, e := range events[seenEvents:] {
				fmt.Fprintf(w, "[%s] %s\n", e.CreatedAt.Format(time.TimeOnly), e.Message)
			}
			seenEvents = len(events)
		}

		switch res.Status {
		case "completed":
			return res, nil
		case "failed":
			return nil, fmt.Errorf("research job %s failed", id)
		}

		time.Sleep(pollInterval)
	}
}
