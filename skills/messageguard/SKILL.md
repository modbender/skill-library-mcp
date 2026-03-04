
### MessageGuard: Outgoing Message Filter Skill

**Purpose**: MessageGuard filters outgoing text to prevent secret leaks and sensitive data exposure by using pattern-based detection and configurable actions (mask, block, or warn).

### Advanced Configuration Options:

- **`mode`**: Determines the global action for matched patterns. Options are:
  - `mask`: Replace sensitive data with the `mask_char`.
  - `block`: Prevent the message from being sent entirely.
  - `warn`: Allow the message but generate warnings.
- **`mask_char`**: The character(s) used to replace sensitive content when `mode` is set to `mask`.
- **`patterns`**: Define or customize regex-based detections. Built-ins exist for API keys, credentials, and more (e.g., AWS keys, JWTs). Add new patterns based on your requirements.
- **`logging`**: Enable detections to be logged as structured JSON for monitoring, debugging, or compliance needs. Configure the `log_path` for the output location.
- **Custom Patterns**: Users can define their custom patterns to override built-ins or extend functionalities. This supports regex and granular action control (mask, block, warn).

**Installation**
1. Clone the repository: `git clone git@github.com:AndrewAndrewsen/MessageGuard.git`.
2. Navigate to the directory. The skill is dependency-free, relying only on the Python standard library.