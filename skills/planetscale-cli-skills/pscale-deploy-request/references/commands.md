Create, review, diff, revert, and manage deploy requests.

This command is only supported for Vitess databases.

Usage:
  pscale deploy-request [command]

Aliases:
  deploy-request, dr

Available Commands:
  apply       Apply changes to a gated deploy request
  cancel      Cancel a deploy request
  close       Close a deploy request
  create      Create a deploy request from a branch
  deploy      Deploy a specific deploy request
  diff        Show the diff of a deploy request
  edit        Edit a deploy request
  list        List all deploy requests for a database
  revert      Revert a deployed deploy request
  review      Review a deploy request (approve, comment, etc...)
  show        Show a specific deploy request
  skip-revert Skip and close a pending deploy request revert

Flags:
  -h, --help         help for deploy-request
      --org string   The organization for the current user

Global Flags:
      --api-token string          The API token to use for authenticating against the PlanetScale API.
      --api-url string            The base URL for the PlanetScale API. (default "https://api.planetscale.com/")
      --config string             Config file (default is $HOME/.config/planetscale/pscale.yml)
      --debug                     Enable debug mode
  -f, --format string             Show output in a specific format. Possible values: [human, json, csv] (default "human")
      --no-color                  Disable color output
      --service-token string      Service Token for authenticating.
      --service-token-id string   The Service Token ID for authenticating.

Use "pscale deploy-request [command] --help" for more information about a command.
