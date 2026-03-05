package cmd

import (
	"fmt"
	"time"

	"github.com/alexrudloff/caesar-cli/internal/output"
	"github.com/spf13/cobra"
)

// chatPollInterval controls how often chat send polls. Tests can set this to 0.
var chatPollInterval = 2 * time.Second

func init() {
	rootCmd.AddCommand(chatCmd)
	chatCmd.AddCommand(chatSendCmd)
	chatCmd.AddCommand(chatHistoryCmd)

	chatSendCmd.Flags().Bool("wait", true, "Wait for response to complete")
}

var chatCmd = &cobra.Command{
	Use:   "chat",
	Short: "Chat with a research job",
}

var chatSendCmd = &cobra.Command{
	Use:   "send [research-id] [message]",
	Short: "Send a follow-up question about a research job",
	Args:  cobra.ExactArgs(2),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		msg, err := c.CreateChatMessage(args[0], args[1])
		if err != nil {
			output.Error("%v", err)
		}

		wait, _ := cmd.Flags().GetBool("wait")
		if !wait {
			output.JSON(msg)
			return
		}

		// Poll until the message is complete.
		w := cmd.OutOrStdout()
		for msg.Status == "processing" {
			time.Sleep(chatPollInterval)
			msg, err = c.GetChatMessage(args[0], msg.ID)
			if err != nil {
				output.Error("%v", err)
			}
		}

		fmt.Fprintln(w, msg.Content)
		if len(msg.Results) > 0 {
			fmt.Fprintln(w, "\nSources:")
			for _, r := range msg.Results {
				fmt.Fprintf(w, "  [%d] %s - %s\n", r.CitationIndex, r.Title, r.URL)
			}
		}
	},
}

var chatHistoryCmd = &cobra.Command{
	Use:   "history [research-id]",
	Short: "List chat history for a research job",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		c, err := newClient()
		if err != nil {
			output.Error("%v", err)
		}

		messages, err := c.GetChatHistory(args[0])
		if err != nil {
			output.Error("%v", err)
		}

		output.JSON(messages)
	},
}
