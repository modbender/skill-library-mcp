---
name: apple-notes-updater
description: Update Apple Notes content by note name using osascript. This skill allows non-interactive updating of note content, preserving formatting and supporting HTML.
---

# Apple Notes Updater

This skill provides a robust, non-interactive way to update the content of an Apple Note by its title. It uses `osascript` to directly interact with the Apple Notes application.

## Usage

The primary function of this skill is to update a note's body.

### Update Note by Title

To update a note, you will need the exact title of the note and the new content (which can include HTML tags for rich text formatting). The skill handles the safe transfer of the content via a temporary file, bypassing command-line argument limitations.

**Example Script Usage:**
```bash
./skills/apple-notes-updater/update_note.sh "My Note Title" "<h1>New Content</h1><p>With <b>HTML</b> formatting.</p>"
```

**Underlying AppleScript Logic:**
```applescript
set noteTitle to "My Note Title"
set newBodyFilePath to (POSIX file "/path/to/temp/file.html") as alias -- Path to a temporary file containing HTML content

tell application "Notes"
    set theNote to first note whose name is noteTitle
    
    set fileRef to open for access newBodyFilePath
    set theContent to read fileRef as «class utf8»
    close access fileRef
    
    set body of theNote to theContent
end tell
```

## Implementation Details

-   Uses `osascript` for direct Apple Notes application control.
-   Content (including HTML) is passed via a temporary file to ensure correct escaping and formatting.
-   Supports HTML within the `newBody` for rich text formatting.
-   Requires Apple Notes.app to be running and accessible.
-   macOS-only.
