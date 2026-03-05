
# SQL Server Toolkit

Command-line toolkit for Microsoft SQL Server.

## Capabilities
- Schema creation
- Versioned migrations
- Index management
- Performance diagnostics
- Backup & restore
- Bulk import/export

## Connect
sqlcmd -S localhost -E
sqlcmd -S localhost -U sa -P YourPassword

## Run Script
sqlcmd -S localhost -d MyDatabase -i script.sql

## Example Table
CREATE TABLE Users (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    Name NVARCHAR(100) NOT NULL,
    CreatedAt DATETIME2 DEFAULT SYSDATETIME()
);

## Example Index
CREATE INDEX IX_Users_Email ON Users(Email);

## Backup Example
BACKUP DATABASE MyDatabase
TO DISK = 'C:\backup\MyDatabase.bak'
WITH FORMAT, INIT;

## Performance Diagnostics
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
