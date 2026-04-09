# Beads CLI Reference (bd / bv)

Beads is a git-backed issue tracking system with Dolt database backend. Two external CLIs.

## bd — Beads CRUD CLI

### Issue Management

```bash
# Create
bd create --title "Fix auth bug" --type=bug --priority=2
bd create --title "Add feature" --type=task --priority=1
bd create --title "..." --type=feature --labels "sprint-1,critical"

# Read
bd show <id>                      # Full details with dependencies
bd show <id> --json               # JSON output
bd list                           # List all issues
bd list --status=open             # Filter by status
bd list --type=task               # Filter by type
bd list --assignee=Toast          # Filter by assignee
bd ready                          # Unblocked issues ready to work

# Update
bd update <id> --title "new title"
bd update <id> --priority=1
bd update <id> --status=in_progress
bd update <id> --assignee=Toast

# Close
bd close <id>                     # Close issue
bd close <id> --reason "Merged in PR #123"
```

### Issue Types
task, bug, feature, epic, decision, event, message, queue, merge_request, agent, chore

### Issue Statuses
open, in_progress, closed (and custom statuses)

### Priority Levels
0 (highest) to 4 (lowest)

### Bead ID Format
prefix + 5-char alphanumeric: `gt-abc12`, `hq-x7k2m`, `bd-q3r5t`

Prefix determines database routing — each rig has its own prefix.

### Dependencies

```bash
bd dep add <from> <to> --type=blocks           # Blocking dependency
bd dep add <from> <to> --type=tracks           # Tracking (convoy)
bd dep add <from> <to> --type=waits-for        # Wait dependency
bd dep add <from> <to> --type=merge-blocks     # Merge blocking
bd dep add <from> <to> --type=conditional-blocks
bd dep remove <from> <to>                       # Remove dependency
```

**Blocking types**: blocks, conditional-blocks, waits-for, merge-blocks
- Unclosed blocking dep = issue is blocked
- `merge-blocks` requires CloseReason starting with "Merged in "
- Parent-child is NOT blocking

### Formulas

```bash
bd formula list                   # List available formulas
bd formula show <name>            # Show formula details
bd cook <formula>                 # Formula → Proto (instantiate)
bd cook <formula> --var key=val   # With variables
```

### Sync & Migration

```bash
bd sync                           # Sync with git
bd migrate --yes                  # Run migrations
bd init --server                  # Initialize with Dolt server mode
```

### Configuration

```bash
bd config set types.custom <csv>       # Set custom types
bd config set status.custom <csv>      # Set custom statuses
bd config get types.custom             # Get custom types
```

## bv — Beads Graph Analysis

```bash
bv --robot-triage                 # Graph-aware ranked picks for agents
```

**WARNING**: Never run bare `bv` without flags — it launches an interactive TUI. Always use `bv --robot-triage` for scripted/agent usage.

## Data Storage

- Issues stored in `.beads/` directory within each rig
- Backed by Dolt databases in `~/gt/.dolt-data/`
- Prefix-based routing maps bead IDs to their home database
- `routes.jsonl` in town root maps prefixes to rig paths

## Key Concepts

### Wisps vs Issues
- **Issues**: Persistent beads (tasks, bugs, features)
- **Wisps**: Ephemeral beads (molecules, patrol records) — auto-expire via TTL

### Labels
Modern type system using labels:
- `gt:agent` — Agent beads
- `gt:task`, `gt:bug`, `gt:feature` — Work items
- `gt:convoy` — Convoy tracking beads
- `gt:merge_request` — Merge requests
- `gt:escalation` — Escalation beads
