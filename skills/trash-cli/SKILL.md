---
name: trash-cli
version: 1.0.5
description: "Use trash-cli to safely delete files by moving them to the system trash instead of permanently removing them. This prevents accidental data loss and allows file recovery. Use instead of rm when you want recoverable deletion."
metadata:
  {
    "openclaw":
      {
        "emoji": "🗑️",
        "requires": { "bins": ["trash-put", "trash-list", "trash-restore", "trash-empty", "trash-rm"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "trash-cli",
              "bins": ["trash-put", "trash-list", "trash-restore", "trash-empty", "trash-rm"],
              "label": "Install trash-cli (brew)",
            },
            {
              "id": "pip",
              "kind": "pip",
              "package": "trash-cli",
              "label": "Install trash-cli (pip)",
            }
          ]
      }
  }
---

# trash-cli

A command line interface to the freedesktop.org trashcan. It trashes files recording the original path, deletion date, and permissions. It uses the same trashcan used by KDE, GNOME, and XFCE.

## Installation

```bash
# Via Homebrew (Linux/macOS)
brew install trash-cli

# Via pip
pip install trash-cli

# Via apt (Debian/Ubuntu)
sudo apt install trash-cli

# Via pacman (Arch Linux)
sudo pacman -S trash-cli

# Via dnf (Fedora)
sudo dnf install trash-cli
```

## Commands Overview

| Command | Description |
|---------|-------------|
| `trash-put` | Move files/directories to trash |
| `trash-list` | List trashed files |
| `trash-restore` | Restore trashed files |
| `trash-empty` | Permanently delete trashed files |
| `trash-rm` | Remove specific files from trash |

## trash-put

Move files or directories to the trash can.

```bash
trash-put <file>           # Trash a file
trash-put <dir>/           # Trash a directory
trash-put -f <file>        # Silently ignore nonexistent files
trash-put -v <file>        # Verbose output
```

### Options

- `-f, --force` - Silently ignore nonexistent files
- `-v, --verbose` - Explain what is being done
- `--trash-dir TRASHDIR` - Use TRASHDIR as trash folder

### Notes

- Unlike `rm`, `trash-put` does not require `-R` for directories
- Files trashed from home partition go to `~/.local/share/Trash/`
- Files from other partitions go to `$partition/.Trash/$uid` or `$partition/.Trash-$uid`

## trash-list

List all trashed files.

```bash
trash-list                          # List all trashed files
trash-list | grep <pattern>         # Search for specific files
trash-list --all-users              # List trashcans of all users
```

### Output Format

```
2008-06-01 10:30:48 /home/user/bar
2008-06-02 21:50:41 /home/user/baz
```

Format: `deletion_date original_path`

## trash-restore

Restore trashed files to their original location.

```bash
trash-restore                       # Interactive restore
trash-restore --overwrite          # Overwrite existing files
trash-restore --sort date          # Sort by date (default)
trash-restore --sort path          # Sort by path
```

### Interactive Mode

```
$ trash-restore
0 2007-08-30 12:36:00 /home/andrea/foo
1 2007-08-30 12:39:41 /home/andrea/bar
2 2007-08-30 12:39:41 /home/andrea/baz
What file to restore [0..2]: 0
```

- Enter the number to restore that file
- Use `0-2,3` to restore multiple files
- Use `--overwrite` to replace existing files

## trash-empty

Permanently remove files from trash.

```bash
trash-empty                 # Remove ALL trashed files
trash-empty 7              # Remove files older than 7 days
trash-empty 1              # Remove files older than 1 day
```

### Examples

```bash
# Delete everything in trash
trash-empty

# Keep only files from the last 7 days
trash-empty 7

# Keep only today's files
trash-empty 1
```

## trash-rm

Remove specific files from trash (by pattern).

```bash
trash-rm <pattern>         # Remove files matching pattern
trash-rm '*.o'             # Remove all .o files
trash-rm foo               # Remove all files named "foo"
trash-rm /full/path        # Remove by original path
```

**Note**: Use quotes to protect pattern from shell expansion.

```bash
trash-rm '*.log'          # Correct
trash-rm *.log            # Wrong - shell will expand
```

## Safety Tips

### Replace rm with trash-put

Add to `.bashrc` or `.zshrc`:

```bash
# Remind yourself not to use rm directly
alias rm='echo "Use trash-put instead!"; false'

# Or use a safer alias
alias rm='trash-put'
```

To bypass the alias when you really need `rm`:

```bash
\rm file.txt
```

### Recovery Workflow

1. Check what's in trash: `trash-list`
2. Find your file: `trash-list | grep <filename>`
3. Restore: `trash-restore`

## Trash Location

- **Home partition**: `~/.local/share/Trash/`
- **Other partitions**: `$mount_point/.Trash/$uid` or `$mount_point/.Trash-$uid`

## Limitations

- Does not support BRTFS volumes
- Cannot trash files from read-only filesystems

## FAQ

### Creating a top-level .Trash directory

If you need to create a trash directory on a different partition:

```bash
sudo mkdir --parent /.Trash
sudo chmod a+rw /.Trash
sudo chmod +t /.Trash
```

### Should I alias rm to trash-put?

**The author advises against this.** Although `trash-put` seems compatible with `rm`, it has different semantics that will cause problems. For example, while `rm` requires `-R` for deleting directories, `trash-put` does not.

Instead, use a warning alias:

```bash
alias rm='echo "This is not the command you are looking for."; false'
```

To bypass when you really need `rm`:

```bash
\rm file.txt
```

## See Also

- [Official GitHub](https://github.com/andreafrancia/trash-cli)
- [FreeDesktop.org Trash Spec](https://specifications.freedesktop.org/trash/latest/)
