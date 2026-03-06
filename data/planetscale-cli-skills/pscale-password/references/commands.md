Create, list, and delete branch passwords.

This command is only supported for Vitess databases.

Usage:
  pscale password [command]

Available Commands:
  create      Create password to access a branch's data
  delete      Delete a branch password
  list        List all passwords of a database
  renew       Renew a branch password

Flags:
  -h, --help         help for password
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

Use "pscale password [command] --help" for more information about a command.
