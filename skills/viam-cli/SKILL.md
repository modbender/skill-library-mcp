---
metadata.openclaw:
  name: "viam-cli-manager"
  description: "Exhaustive Viam CLI interface for managing fleets, modules, machine data, and handling initial CLI installation."
  requires:
    anyBins: ["viam", "brew"]
  disable-model-invocation: false
---

# Comprehensive Viam CLI Management Skill

This skill allows the agent to interact with the Viam robotics platform across all available CLI surfaces, including initial setup, deployment, data management, and the local developer loop.

## Security & Scoping Guardrails
* **No hardcoded credentials:** Never ask the user to paste an API key or Token into the chat. Rely on OpenClaw's environment variable injection. If unauthenticated, instruct the user to run `viam login` in their secure terminal.
* **Read-first approach:** Always prefer listing resources (e.g., `list`, `describe`) before attempting mutations or deletions.
* **Destructive operations:** Always confirm with the user before running any `delete` command across datasets, data pipelines, or machine data.

---

## Initialization & Installation (First-Time Setup)

Before attempting to run any `viam` commands, verify if the CLI is installed by running `viam version` or checking the system path. 

**If the `viam` CLI is NOT installed:**
1. **STOP and ask for permission:** You must explicitly ask the user: *"The Viam CLI is not installed on your system. Would you like me to install it via Homebrew?"*
2. **Execute Installation (Upon Approval Only):** If the user grants permission, run the following commands sequentially:
   * `brew tap viamrobotics/brews`
   * `brew install viam`
3. **Verify:** Once installed, run `viam version` to confirm success, then instruct the user to run `viam login` to authenticate.

---

## Complete Viam CLI Command Reference

### Authentication & Profiles
* `viam login` - Authenticates the session (opens a browser or returns a URL).
* `viam login api-key --key-id <id> --key <secret>` - Authenticates non-interactively via API key.
* `viam logout` - Logs out of the current Viam session.
* `viam whoami` - Displays the current authenticated profile/user.
* `viam profiles` - Manages local CLI profiles.

### Organizations & Locations
* `viam organizations list` - Lists all organizations the user has access to.
* `viam locations list` - Lists locations belonging to an organization.

### Fleet & Machine Management (Aliases: `machine`, `robots`)
* `viam machines list` - Lists all machines in an organization/location.
* `viam machines logs` - Retrieves logs from a specific machine for debugging.
* `viam machines api-key create` - Generates a new machine part API key for programmatic access.
* `viam machines part shell --organization=<org> --location=<loc> --machine=<id>` - Opens a remote shell to a specific machine part (Requires the `ViamShellDanger` fragment on the machine).
* `viam machines part cp` - Copies files to/from a remote machine over Viam's WebRTC tunnel.

### Modules, Hot-Reloading, & Registry
* `viam module generate` - Interactively scaffolds a new module. Can bypass prompts using flags.
* `viam module reload --part-id <machine-part-id>` - **(Hot Reloading)** Bundles local module code, deploys it to the target machine via WebRTC, registers it as a local module, and restarts it.
* `viam module local-app-testing --app-url <url>` - Tests a custom Viam web application locally against machine data.
* `viam module create` - Creates the module entity in the Viam cloud registry.
* `viam module upload --version <version> --platform <platform> <module-path>` - Bundles and uploads a finished module to the Viam Registry.
* `viam packages` - Manages individual software packages.

### Machine Data (Uploads, Syncs, & Databases)
* `viam data export tabular` - Exports sensor/tabular data to a specified destination.
* `viam data export binary` - Exports image/binary data to a specified destination.
* `viam data delete tabular` - Deletes tabular data from the Viam Cloud.
* `viam data delete binary` - Deletes binary data from the Viam Cloud.
* `viam data tag` - Adds or removes tags from data matching specific IDs.
* `viam data database configure` - Creates/modifies a database user for MongoDB Atlas Data Federation.
* `viam data database hostname` - Retrieves the MongoDB Atlas Data Federation hostname.

### Datasets (For Machine Learning)
* `viam dataset create` - Creates a new dataset.
* `viam dataset rename` - Renames an existing dataset.
* `viam dataset list` - Lists datasets for an organization or by specific IDs.
* `viam dataset delete` - Deletes a specified dataset.
* `viam dataset data add` - Adds images/binary data to a dataset.
* `viam dataset data remove` - Removes images/binary data from a dataset.
* `viam dataset export` - Downloads all data contained within a dataset.

### Data Pipelines (Precompute & Transformations)
* `viam datapipelines create` - Creates a new data pipeline.
* `viam datapipelines describe` - Gets detailed information about a specific data pipeline.
* `viam datapipelines delete` - Deletes a data pipeline.
* `viam datapipelines enable` - Resumes executing a disabled data pipeline.
* `viam datapipelines disable` - Stops executing a data pipeline without deleting it.
* `viam datapipelines list` - Lists all data pipelines in an organization.

### Machine Learning (Training & Inference)
* `viam train` - Initiates an ML model training job in the Viam cloud.
* `viam training-script` - Manages scripts utilized during custom ML training runs.
* `viam infer` - Runs quick inferences against a model directly from the CLI.

### Metadata & Diagnostics
* `viam metadata` - Retrieves metadata related to the Viam configuration or platform state.
* `viam parse-ftdc` - Parses Full-Time Data Capture (FTDC) diagnostic data files generated by `viam-server`.
* `viam version` - Prints the currently installed version of the Viam CLI.

---

## ⚠️ Fallback & Troubleshooting Protocol (CRITICAL)

The Viam platform evolves rapidly. **If any `viam` command fails, returns a syntax error, or complains about an unrecognized flag, you MUST adhere to the following fallback protocol:**

1. **Read the local help text:** Immediately run `--help` on the failing command or subcommand (e.g., `viam module reload --help` or `viam datapipelines --help`) to read the exact syntax required by the user's installed binary.
2. **Suggest an Upgrade:** If a requested root command or feature does not exist locally, the user is likely running an outdated version. Advise them to upgrade by explicitly asking for permission to run `brew upgrade viam`.
3. **Do not hallucinate flags:** Never guess a flag or command structure. Always defer to the local CLI's help output if execution fails.
