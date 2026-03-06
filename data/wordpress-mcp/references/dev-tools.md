# Developer Tools Reference

Theme and plugin file management, and direct database queries.

## Theme Management

### wp_list_themes
List installed themes with status.

### wp_switch_theme
- `stylesheet` (string, required): Theme directory name

### wp_create_theme
Create a new theme from scratch.
- `name` (string, required)
- `template` (string): Parent theme for child themes

### wp_copy_theme
- `source` (string, required): Source theme slug
- `name` (string, required): New theme name

### wp_rename_theme
- `old_name` (string, required)
- `new_name` (string, required)

### wp_delete_theme
- `stylesheet` (string, required)

### wp_theme_mkdir
Create a directory in a theme.
- `theme` (string, required)
- `path` (string, required)

### wp_theme_list_dir
List files in a theme directory.
- `theme` (string, required)
- `path` (string): Subdirectory (default: root)

### wp_theme_get_file
Read a theme file's contents.
- `theme` (string, required)
- `path` (string, required)

### wp_theme_put_file
Write/create a file in a theme.
- `theme` (string, required)
- `path` (string, required)
- `content` (string, required)

### wp_theme_alter_file
Search-replace in a theme file.
- `theme` (string, required)
- `path` (string, required)
- `search` (string, required)
- `replace` (string, required)

### wp_theme_delete_path
Delete a file/directory in a theme.
- `theme` (string, required)
- `path` (string, required)

### wp_theme_set_screenshot
Set theme screenshot image.
- `theme` (string, required)
- `url` (string, required): Image URL

## Plugin Management

### wp_list_plugins_detailed
Detailed plugin list with file paths, versions, active status.

### wp_activate_plugin
- `plugin` (string, required): Plugin file path (e.g. "ai-engine/ai-engine.php")

### wp_deactivate_plugin
- `plugin` (string, required)

### wp_create_plugin
Create a new plugin.
- `name` (string, required)
- `slug` (string)

### wp_copy_plugin
- `source` (string, required)
- `name` (string, required)

### wp_rename_plugin
- `old_name` (string, required)
- `new_name` (string, required)

### wp_delete_plugin
- `plugin` (string, required)

### wp_plugin_mkdir
- `plugin` (string, required): Plugin slug
- `path` (string, required)

### wp_plugin_list_dir
- `plugin` (string, required)
- `path` (string)

### wp_plugin_get_file
- `plugin` (string, required)
- `path` (string, required)

### wp_plugin_put_file
- `plugin` (string, required)
- `path` (string, required)
- `content` (string, required)

### wp_plugin_alter_file
- `plugin` (string, required)
- `path` (string, required)
- `search` (string, required)
- `replace` (string, required)

### wp_plugin_delete_path
- `plugin` (string, required)
- `path` (string, required)

## Database

### wp_db_query
Run a direct SQL query. **Use with extreme caution.**
- `query` (string, required): SQL query
- Returns results for SELECT queries, affected rows for UPDATE/INSERT/DELETE.

⚠️ **Safety**: Only use for read queries unless explicitly asked. Never DROP tables or modify core WP tables without confirmation.
