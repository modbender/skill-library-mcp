List, show, and switch organizations

Usage:
  pscale org [command]

Available Commands:
  list        List the currently active organizations
  show        Display the currently active organization
  switch      Switch the currently active organization

Flags:
  -h, --help   help for org

Global Flags:
      --api-token string          The API token to use for authenticating against the PlanetScale API.
      --api-url string            The base URL for the PlanetScale API. (default "https://api.planetscale.com/")
      --config string             Config file (default is $HOME/.config/planetscale/pscale.yml)
      --debug                     Enable debug mode
  -f, --format string             Show output in a specific format. Possible values: [human, json, csv] (default "human")
      --no-color                  Disable color output
      --service-token string      Service Token for authenticating.
      --service-token-id string   The Service Token ID for authenticating.

Use "pscale org [command] --help" for more information about a command.
