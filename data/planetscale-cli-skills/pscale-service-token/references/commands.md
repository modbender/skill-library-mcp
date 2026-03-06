Create, list, and manage access for service tokens

Usage:
  pscale service-token [command]

Available Commands:
  add-access    add access to a service token in the organization
  create        create a service token for the organization
  delete        delete an entire service token in an organization
  delete-access delete access granted to a service token in the organization
  list          list service tokens for the organization
  show-access   fetch a service token and its accesses

Flags:
  -h, --help         help for service-token
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

Use "pscale service-token [command] --help" for more information about a command.
