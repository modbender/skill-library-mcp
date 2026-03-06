
# SQL Server Toolkit

CLI toolkit for managing Microsoft SQL Server databases.
Includes schema design, migrations, indexing, performance tuning, and backup/restore scripts.

## Requirements
- sqlcmd
- bcp
- Microsoft SQL Server

## Example Connection
sqlcmd -S localhost -E

## Run Script
sqlcmd -S localhost -d MyDatabase -i script.sql
