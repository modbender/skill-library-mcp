Create, delete, diff, and manage branches

Usage:
  pscale branch [command]

Available Commands:
  create          Create a new branch from a database
  delete          Delete a branch from a database
  demote          Demote a production branch to development
  diff            Show the diff of a branch
  lint            Lints the schema for a branch
  list            List all branches of a database
  promote         Promote a new branch from a database
  refresh-schema  Refresh the schema for a database branch
  routing-rules   Fetch or update your keyspace routing rules
  safe-migrations Enable or disable safe migrations on a branch
  schema          Show the schema of a branch
  show            Show a specific branch of a database
  switch          Switches the current project to use the specified branch

Flags:
  -h, --help         help for branch
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

Use "pscale branch [command] --help" for more information about a command.
