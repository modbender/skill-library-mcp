OpenClaw Skill: openkm-rest

Local OpenKM REST integration (no SOAP, no CMIS).

Required ENV:
  OPENKM_BASE_URL (WITHOUT /OpenKM)
  OPENKM_USERNAME
  OPENKM_PASSWORD

Optional:
  OPENKM_DEBUG=1

FOLDER OPERATIONS:
  list              List folder contents
  ensure-structure  Create folder structure (creates missing parent folders)

DOCUMENT OPERATIONS:
  upload            Upload a document
  download          Download a document
  move              Move a document to another folder
  rename            Rename a document
  delete            Delete a document

METADATA & ORGANIZATION:
  properties        Get document properties (title, description, keywords, etc.)
  set-properties    Update title and/or description
  add-keyword       Add a keyword tag
  remove-keyword    Remove a keyword tag
  add-category      Add a category
  remove-category   Remove a category

VERSIONING:
  versions          Get document version history
  download-version  Download a specific version
  restore-version   Restore document to a previous version

SEARCH:
  search-content    Full-text search by content
  search-name       Search by filename
  search-keywords   Search by keywords (comma-separated)
  search            General search with multiple filters

WORKFLOWS:
  workflows         List available workflows (requires workflow config)
  start-workflow    Start a workflow for a document
  tasks             List tasks (by document or actor)
  complete-task     Complete a workflow task
  comment-task      Add comment to a task
  assign-task       Assign task to actor

Examples:
  python3 openkm_cli.py list --folder-path /okm:root
  python3 openkm_cli.py ensure-structure --parts Folder1 Subfolder
  python3 openkm_cli.py upload --okm-path /okm:root/folder/file.pdf --local-path /path/file.pdf
  python3 openkm_cli.py properties --doc-id <uuid>
  python3 openkm_cli.py set-properties --doc-id <uuid> --title "My Title" --description "My desc"
  python3 openkm_cli.py add-keyword --doc-id <uuid> --keyword "Invoice"
  python3 openkm_cli.py versions --doc-id <uuid>
  python3 openkm_cli.py search-content --content "server hosting"
  python3 openkm_cli.py search-keywords --keywords "Invoice,Hosting"
  python3 openkm_cli.py workflows
  python3 openkm_cli.py tasks --actor-id john.doe
