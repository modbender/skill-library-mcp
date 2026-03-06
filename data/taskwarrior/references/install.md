# Taskwarrior availability (ClawHub-friendly)

This skill **does not install Taskwarrior at runtime**.

## Requirement
Taskwarrior must be present in the runtime environment.

## Validation
- `task --version`

## If missing
Ask the environment/runtime owner to install Taskwarrior in the base image:

- Debian/Ubuntu: `taskwarrior`
- Fedora/RHEL (varies): `task` or `taskwarrior`
- Arch: `task`
- macOS (local dev): `task` (Homebrew)

Once installed, re-run `task --version` and proceed.
