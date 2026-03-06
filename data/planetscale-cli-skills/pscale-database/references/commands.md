Create, read, delete, and dump/restore databases

Usage:
  pscale database [command]

Aliases:
  database, db

Available Commands:
  create       Create a database instance
  delete       Delete a database instance
  dump         Backup and dump your database (Vitess databases only)
  list         List databases
  restore-dump Restore your database from a local dump directory (Vitess databases only)
  show         Retrieve information about a database

Flags:
  -h, --help         help for database
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

Use "pscale database [command] --help" for more information about a command.
