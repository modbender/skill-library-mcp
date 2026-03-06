#!/bin/sh
# CLI tool to manage macOS Reminders.
# Outputs JSON. Usage: reminders <command> [options]

set -e

# ─────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────

print_usage() {
  echo "Usage: reminders <command> [options]"
  echo ""
  echo "Commands:"
  echo "  lists                              Show all reminder lists"
  echo "  ls [<list>] [--all]                List reminders (default: incomplete only)"
  echo "  search <query> [--all]             Search reminders by name"
  echo "  add --name <text> [options]        Create a reminder"
  echo "  complete <query> [--list <name>]   Mark a reminder as complete"
  echo "  edit <query> [options]             Edit a reminder"
  echo "  delete <query> [--yes]             Delete a reminder"
  echo "  add-list --name <name>             Create a new list"
  echo ""
  echo "Run 'reminders <command> --help' for command details."
}

print_ls_help() {
  echo "Usage: reminders ls [<list-name>] [--all]"
  echo ""
  echo "List reminders. By default shows only incomplete reminders."
  echo "If no list name is given, shows reminders across all lists."
  echo ""
  echo "Options:"
  echo "  --all    Include completed reminders"
  echo ""
  echo "Examples:"
  echo "  reminders ls"
  echo "  reminders ls \"Shopping\""
  echo "  reminders ls --all"
}

print_search_help() {
  echo "Usage: reminders search <query> [--all]"
  echo "       reminders <query>          (search is the default command)"
  echo ""
  echo "Search reminders by name and notes across all lists."
  echo "By default shows only incomplete matches."
  echo ""
  echo "Options:"
  echo "  --all    Include completed reminders"
  echo ""
  echo "Examples:"
  echo "  reminders search \"buy milk\""
  echo "  reminders \"dentist\""
  echo "  reminders search \"groceries\" --all"
}

print_add_help() {
  echo "Usage: reminders add --name <text> [options]"
  echo ""
  echo "Options:"
  echo "  --name <text>         Reminder name (required)"
  echo "  --list <name>         Target list (default: default list)"
  echo "  --due <datetime>      Due date (ISO 8601, e.g. 2025-02-15T10:00:00)"
  echo "  --remind <datetime>   Remind-me date (ISO 8601)"
  echo "  --notes <text>        Notes / body text"
  echo "  --priority <level>    high, medium, low, or none (default: none)"
  echo "  --flagged             Mark as flagged"
  echo ""
  echo "If --due is set without --remind, remind-me date defaults to the due date."
  echo ""
  echo "Examples:"
  echo "  reminders add --name \"Buy milk\""
  echo "  reminders add --name \"Call dentist\" --due 2025-02-15T09:00:00 --priority high"
  echo "  reminders add --name \"Pick up package\" --list \"Errands\" --notes \"At post office\""
}

print_complete_help() {
  echo "Usage: reminders complete <query> [--list <name>]"
  echo ""
  echo "Mark a reminder as complete. Searches incomplete reminders by name."
  echo "If multiple reminders match, lists them so you can be more specific."
  echo ""
  echo "Options:"
  echo "  --list <name>    Narrow search to a specific list"
  echo ""
  echo "Examples:"
  echo "  reminders complete \"Buy milk\""
  echo "  reminders complete \"Buy milk\" --list \"Shopping\""
}

print_edit_help() {
  echo "Usage: reminders edit <query> [options]"
  echo ""
  echo "Find a reminder by name and apply changes."
  echo "If multiple reminders match, lists them and exits."
  echo ""
  echo "Options:"
  echo "  --list <name>         Narrow search to a specific list"
  echo "  --name <text>         Set new name"
  echo "  --due <datetime>      Set due date (ISO 8601, or \"clear\" to remove)"
  echo "  --remind <datetime>   Set remind-me date (ISO 8601, or \"clear\" to remove)"
  echo "  --notes <text>        Set notes (or \"clear\" to remove)"
  echo "  --priority <level>    Set priority (high, medium, low, none)"
  echo "  --flagged             Set flagged"
  echo "  --unflagged           Remove flag"
  echo "  --uncomplete          Mark as incomplete"
  echo ""
  echo "Examples:"
  echo "  reminders edit \"Buy milk\" --name \"Buy almond milk\""
  echo "  reminders edit \"Call dentist\" --due 2025-02-20T14:00:00"
  echo "  reminders edit \"Old task\" --uncomplete"
}

print_delete_help() {
  echo "Usage: reminders delete <query> [--list <name>] [--yes]"
  echo ""
  echo "Find a reminder by name and delete it."
  echo "If multiple reminders match, lists them and exits."
  echo "Asks for confirmation unless --yes is passed."
  echo ""
  echo "Options:"
  echo "  --list <name>    Narrow search to a specific list"
  echo "  --yes            Skip confirmation prompt"
  echo ""
  echo "Examples:"
  echo "  reminders delete \"Buy milk\" --yes"
  echo "  reminders delete \"Old task\" --list \"Shopping\" --yes"
}

print_add_list_help() {
  echo "Usage: reminders add-list --name <text>"
  echo ""
  echo "Create a new reminder list."
  echo ""
  echo "Examples:"
  echo "  reminders add-list --name \"Projects\""
}

# ─────────────────────────────────────────────
# JXA helpers (embedded in each osascript call)
# ─────────────────────────────────────────────

JXA_HELPERS=$(cat <<'HELPEOF'
function safeDate(d) {
  try { if (d && typeof d.toISOString === "function") return d.toISOString(); } catch(e) {}
  return null;
}

function serializeReminder(r, listName) {
  var priorityMap = {0: "none", 1: "high", 5: "medium", 9: "low"};
  var p = 0; try { p = r.priority(); } catch(e) {}
  var flagged = false; try { flagged = r.flagged(); } catch(e) {}
  return {
    name: r.name() || "",
    body: r.body() || "",
    completed: r.completed(),
    dueDate: safeDate(r.dueDate()),
    remindMeDate: safeDate(r.remindMeDate()),
    completionDate: safeDate(r.completionDate()),
    priority: priorityMap[p] || "none",
    flagged: flagged,
    list: listName
  };
}

function findList(app, name) {
  var lists = app.lists();
  var lower = name.toLowerCase();
  for (var i = 0; i < lists.length; i++) {
    if (lists[i].name().toLowerCase() === lower) return lists[i];
  }
  return null;
}

function findReminders(app, query, listFilter, includeCompleted) {
  var q = query.toLowerCase();
  var searchLists;
  if (listFilter) {
    var l = findList(app, listFilter);
    searchLists = l ? [l] : [];
  } else {
    searchLists = app.lists();
  }
  var results = [];
  for (var i = 0; i < searchLists.length; i++) {
    var list = searchLists[i];
    var reminders = list.reminders();
    for (var j = 0; j < reminders.length; j++) {
      var r = reminders[j];
      if (!includeCompleted && r.completed()) continue;
      var name = (r.name() || "").toLowerCase();
      if (name.includes(q)) {
        results.push({ reminder: r, listName: list.name() });
      }
    }
  }
  return results;
}
HELPEOF
)

# ─────────────────────────────────────────────
# Lists
# ─────────────────────────────────────────────

cmd_lists() {
  if [ "$1" = "--help" ]; then
    echo "Usage: reminders lists"
    echo ""
    echo "Show all reminder lists with counts."
    exit 0
  fi

  osascript -l JavaScript <<JXAEOF
var app = Application("Reminders");
var lists = app.lists();
var results = [];
for (var i = 0; i < lists.length; i++) {
  var list = lists[i];
  var reminders = list.reminders();
  var incomplete = 0;
  for (var j = 0; j < reminders.length; j++) {
    if (!reminders[j].completed()) incomplete++;
  }
  results.push({
    name: list.name(),
    count: reminders.length,
    incomplete: incomplete
  });
}
JSON.stringify(results, null, 2);
JXAEOF
}

# ─────────────────────────────────────────────
# Ls
# ─────────────────────────────────────────────

cmd_ls() {
  SHOW_ALL=""
  LIST_NAME=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --all)  SHOW_ALL="1"; shift ;;
      --help) print_ls_help; exit 0 ;;
      *)      LIST_NAME="$1"; shift ;;
    esac
  done

  osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");
var showAll = "$SHOW_ALL" === "1";
var listFilter = "$LIST_NAME";
var results = [];

if (listFilter) {
  var list = findList(app, listFilter);
  if (!list) {
    JSON.stringify({ error: "List not found: " + listFilter }, null, 2);
  } else {
    var reminders = list.reminders();
    for (var i = 0; i < reminders.length; i++) {
      if (!showAll && reminders[i].completed()) continue;
      results.push(serializeReminder(reminders[i], list.name()));
    }
    JSON.stringify(results, null, 2);
  }
} else {
  var lists = app.lists();
  for (var i = 0; i < lists.length; i++) {
    var list = lists[i];
    var reminders = list.reminders();
    for (var j = 0; j < reminders.length; j++) {
      if (!showAll && reminders[j].completed()) continue;
      results.push(serializeReminder(reminders[j], list.name()));
    }
  }
  JSON.stringify(results, null, 2);
}
JXAEOF
}

# ─────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────

cmd_search() {
  SHOW_ALL=""
  QUERY=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --all)  SHOW_ALL="1"; shift ;;
      --help) print_search_help; exit 0 ;;
      *)
        if [ -z "$QUERY" ]; then
          QUERY="$1"
        else
          QUERY="$QUERY $1"
        fi
        shift ;;
    esac
  done

  if [ -z "$QUERY" ]; then
    print_search_help
    exit 1
  fi

  osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");
var showAll = "$SHOW_ALL" === "1";
var query = "$QUERY".toLowerCase();
var results = [];

var lists = app.lists();
for (var i = 0; i < lists.length; i++) {
  var list = lists[i];
  var reminders = list.reminders();
  for (var j = 0; j < reminders.length; j++) {
    var r = reminders[j];
    if (!showAll && r.completed()) continue;
    var name = (r.name() || "").toLowerCase();
    var body = (r.body() || "").toLowerCase();
    if (name.includes(query) || body.includes(query)) {
      results.push(serializeReminder(r, list.name()));
    }
  }
}
JSON.stringify(results, null, 2);
JXAEOF
}

# ─────────────────────────────────────────────
# Add
# ─────────────────────────────────────────────

cmd_add() {
  NAME="" LIST_NAME="" DUE="" REMIND="" NOTES="" PRIORITY="" FLAGGED=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --name)     NAME="$2";      shift 2 ;;
      --list)     LIST_NAME="$2"; shift 2 ;;
      --due)      DUE="$2";       shift 2 ;;
      --remind)   REMIND="$2";    shift 2 ;;
      --notes)    NOTES="$2";     shift 2 ;;
      --priority) PRIORITY="$2";  shift 2 ;;
      --flagged)  FLAGGED="1";    shift ;;
      --help)     print_add_help; exit 0 ;;
      *)          echo "Unknown option: $1"; print_add_help; exit 1 ;;
    esac
  done

  if [ -z "$NAME" ]; then
    echo "Error: --name is required."
    echo ""
    print_add_help
    exit 1
  fi

  osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");

(function() {
  var listName = "$LIST_NAME";
  var targetList;
  if (listName) {
    targetList = findList(app, listName);
    if (!targetList) return JSON.stringify({ error: "List not found: " + listName }, null, 2);
  } else {
    targetList = app.defaultList();
  }

  var priorityMap = { "high": 1, "medium": 5, "low": 9, "none": 0 };
  var props = { name: "$NAME" };

  var notes = "$NOTES";
  if (notes) props.body = notes;

  var due = "$DUE";
  if (due) {
    props.dueDate = new Date(due);
    var remind = "$REMIND";
    props.remindMeDate = remind ? new Date(remind) : new Date(due);
  } else {
    var remind = "$REMIND";
    if (remind) props.remindMeDate = new Date(remind);
  }

  var prio = "$PRIORITY";
  if (prio && priorityMap[prio] !== undefined) props.priority = priorityMap[prio];

  if ("$FLAGGED" === "1") props.flagged = true;

  var r = app.Reminder(props);
  targetList.reminders.push(r);

  var result = serializeReminder(r, targetList.name());
  result.created = true;
  return JSON.stringify(result, null, 2);
})();
JXAEOF
}

# ─────────────────────────────────────────────
# Complete
# ─────────────────────────────────────────────

cmd_complete() {
  if [ -z "$1" ] || [ "$1" = "--help" ]; then
    print_complete_help
    [ "$1" = "--help" ] && exit 0 || exit 1
  fi

  QUERY=""
  LIST_NAME=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --list) LIST_NAME="$2"; shift 2 ;;
      *)
        if [ -z "$QUERY" ]; then
          QUERY="$1"
        else
          QUERY="$QUERY $1"
        fi
        shift ;;
    esac
  done

  osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");

(function() {
  var query = "$QUERY";
  var listFilter = "$LIST_NAME";
  var matches = findReminders(app, query, listFilter, false);

  if (matches.length === 0) {
    return JSON.stringify({ error: "No incomplete reminders found matching: " + query }, null, 2);
  } else if (matches.length > 1) {
    return JSON.stringify({
      error: "Multiple reminders match. Be more specific.",
      matches: matches.map(function(m) { return { name: m.reminder.name(), list: m.listName }; })
    }, null, 2);
  }

  var r = matches[0].reminder;
  r.completed = true;
  return JSON.stringify(serializeReminder(r, matches[0].listName), null, 2);
})();
JXAEOF
}

# ─────────────────────────────────────────────
# Edit
# ─────────────────────────────────────────────

cmd_edit() {
  if [ -z "$1" ] || [ "$1" = "--help" ]; then
    print_edit_help
    [ "$1" = "--help" ] && exit 0 || exit 1
  fi

  QUERY="$1"; shift
  LIST_NAME="" SET_NAME="" SET_DUE="" SET_REMIND="" SET_NOTES="" SET_PRIORITY=""
  SET_FLAGGED="" SET_UNFLAGGED="" SET_UNCOMPLETE=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --list)       LIST_NAME="$2";     shift 2 ;;
      --name)       SET_NAME="$2";      shift 2 ;;
      --due)        SET_DUE="$2";       shift 2 ;;
      --remind)     SET_REMIND="$2";    shift 2 ;;
      --notes)      SET_NOTES="$2";     shift 2 ;;
      --priority)   SET_PRIORITY="$2";  shift 2 ;;
      --flagged)    SET_FLAGGED="1";    shift ;;
      --unflagged)  SET_UNFLAGGED="1";  shift ;;
      --uncomplete) SET_UNCOMPLETE="1"; shift ;;
      *)            echo "Unknown option: $1"; print_edit_help; exit 1 ;;
    esac
  done

  osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");

(function() {
  var query = "$QUERY";
  var listFilter = "$LIST_NAME";
  var matches = findReminders(app, query, listFilter, true);

  if (matches.length === 0) {
    return JSON.stringify({ error: "No reminders found matching: " + query }, null, 2);
  } else if (matches.length > 1) {
    return JSON.stringify({
      error: "Multiple reminders match. Be more specific.",
      matches: matches.map(function(m) {
        return { name: m.reminder.name(), list: m.listName, completed: m.reminder.completed() };
      })
    }, null, 2);
  }

  var r = matches[0].reminder;

  var setName = "$SET_NAME";
  if (setName) r.name = setName;

  var setDue = "$SET_DUE";
  if (setDue === "clear") r.dueDate = null;
  else if (setDue) r.dueDate = new Date(setDue);

  var setRemind = "$SET_REMIND";
  if (setRemind === "clear") r.remindMeDate = null;
  else if (setRemind) r.remindMeDate = new Date(setRemind);

  var setNotes = "$SET_NOTES";
  if (setNotes === "clear") r.body = "";
  else if (setNotes) r.body = setNotes;

  var setPriority = "$SET_PRIORITY";
  var priorityMap = { "high": 1, "medium": 5, "low": 9, "none": 0 };
  if (setPriority && priorityMap[setPriority] !== undefined) r.priority = priorityMap[setPriority];

  if ("$SET_FLAGGED" === "1") r.flagged = true;
  if ("$SET_UNFLAGGED" === "1") r.flagged = false;
  if ("$SET_UNCOMPLETE" === "1") r.completed = false;

  var result = serializeReminder(r, matches[0].listName);
  result.updated = true;
  return JSON.stringify(result, null, 2);
})();
JXAEOF
}

# ─────────────────────────────────────────────
# Delete
# ─────────────────────────────────────────────

cmd_delete() {
  if [ -z "$1" ] || [ "$1" = "--help" ]; then
    print_delete_help
    [ "$1" = "--help" ] && exit 0 || exit 1
  fi

  SKIP_CONFIRM=""
  QUERY=""
  LIST_NAME=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --yes)  SKIP_CONFIRM="1"; shift ;;
      --list) LIST_NAME="$2"; shift 2 ;;
      *)
        if [ -z "$QUERY" ]; then
          QUERY="$1"
        else
          QUERY="$QUERY $1"
        fi
        shift ;;
    esac
  done

  if [ -z "$QUERY" ]; then
    echo "Error: no search query provided."
    print_delete_help
    exit 1
  fi

  # First, find matching reminder(s)
  MATCH_RESULT=$(osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");

(function() {
  var query = "$QUERY";
  var listFilter = "$LIST_NAME";
  var matches = findReminders(app, query, listFilter, true);

  return JSON.stringify({
    count: matches.length,
    matches: matches.map(function(m) {
      return { name: m.reminder.name(), list: m.listName };
    })
  });
})();
JXAEOF
  )

  MATCH_COUNT=$(echo "$MATCH_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])")

  if [ "$MATCH_COUNT" = "0" ]; then
    echo "{\"error\": \"No reminders found matching: $QUERY\"}"
    exit 1
  elif [ "$MATCH_COUNT" != "1" ]; then
    echo "$MATCH_RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(json.dumps({'error': 'Multiple reminders match. Be more specific.', 'matches': d['matches']}, indent=2))
"
    exit 1
  fi

  MATCH_NAME=$(echo "$MATCH_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['matches'][0]['name'])")
  MATCH_LIST=$(echo "$MATCH_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['matches'][0]['list'])")

  # Confirm
  if [ -z "$SKIP_CONFIRM" ]; then
    printf "Delete \"%s\" from \"%s\"? [y/N] " "$MATCH_NAME" "$MATCH_LIST"
    read -r REPLY
    case "$REPLY" in
      y|Y|yes|YES) ;;
      *) echo "Cancelled."; exit 0 ;;
    esac
  fi

  # Delete
  osascript -l JavaScript <<JXAEOF
$JXA_HELPERS

var app = Application("Reminders");

(function() {
  var query = "$QUERY";
  var listFilter = "$LIST_NAME";
  var matches = findReminders(app, query, listFilter, true);

  if (matches.length === 1) {
    var name = matches[0].reminder.name();
    app.delete(matches[0].reminder);
    return JSON.stringify({ deleted: true, name: name, list: matches[0].listName }, null, 2);
  }
  return JSON.stringify({ error: "Could not find the reminder to delete." }, null, 2);
})();
JXAEOF
}

# ─────────────────────────────────────────────
# Add List
# ─────────────────────────────────────────────

cmd_add_list() {
  NAME=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --name) NAME="$2"; shift 2 ;;
      --help) print_add_list_help; exit 0 ;;
      *)      echo "Unknown option: $1"; print_add_list_help; exit 1 ;;
    esac
  done

  if [ -z "$NAME" ]; then
    echo "Error: --name is required."
    echo ""
    print_add_list_help
    exit 1
  fi

  osascript -l JavaScript <<JXAEOF
var app = Application("Reminders");
var newList = app.List({ name: "$NAME" });
app.lists.push(newList);
JSON.stringify({ created: true, name: newList.name() }, null, 2);
JXAEOF
}

# ─────────────────────────────────────────────
# Route subcommand
# ─────────────────────────────────────────────

case "$1" in
  lists)    shift; cmd_lists "$@" ;;
  ls)       shift; cmd_ls "$@" ;;
  search)   shift; cmd_search "$@" ;;
  add)      shift; cmd_add "$@" ;;
  complete) shift; cmd_complete "$@" ;;
  edit)     shift; cmd_edit "$@" ;;
  delete)   shift; cmd_delete "$@" ;;
  add-list) shift; cmd_add_list "$@" ;;
  --help|-h|"") print_usage; exit 0 ;;
  # Default: treat as search query
  *)        cmd_search "$@" ;;
esac
