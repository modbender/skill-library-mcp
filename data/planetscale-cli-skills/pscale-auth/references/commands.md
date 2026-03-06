Manage authentication

Usage:
  pscale auth [command]

Available Commands:
  check       Check if you are authenticated
  login       Authenticate with the PlanetScale API
  logout      Log out of the PlanetScale API

Flags:
  -h, --help   help for auth

Global Flags:
      --api-token string          The API token to use for authenticating against the PlanetScale API.
      --api-url string            The base URL for the PlanetScale API. (default "https://api.planetscale.com/")
      --config string             Config file (default is $HOME/.config/planetscale/pscale.yml)
      --debug                     Enable debug mode
  -f, --format string             Show output in a specific format. Possible values: [human, json, csv] (default "human")
      --no-color                  Disable color output
      --service-token string      Service Token for authenticating.
      --service-token-id string   The Service Token ID for authenticating.

Use "pscale auth [command] --help" for more information about a command.
