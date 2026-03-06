# Changelog

## 0.1.0 - Initial
- Package created from SKILL.md: includes scripts/, references/, assets/ placeholders and packaging metadata.

## 0.1.1 and 0.1.2 - Fixes
- Update name to "zotero-skill"

## 0.1.3 - Update changelog
- Add changelog file and update with previous changes.

## 0.1.4 - Use the environment variable for the API key
- Update the code to check if the environment variable `ZOTERO_API_KEY` is set and use it if available, instead of requiring the user to pass it as a command-line argument. This allows for more secure handling of API keys and simplifies usage by eliminating the need to provide the key with every command.

# 0.1.5 - Update skill metadata
- Update the skill metadata to reflect the new requirement for environment variables and provide an example configuration.
- Change the name back to "zotero".
