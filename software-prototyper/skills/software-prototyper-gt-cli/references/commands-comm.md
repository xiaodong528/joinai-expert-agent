# Communication Commands

## mail — Agent messaging system

### Core Operations
```bash
gt mail inbox [address]           # Check inbox
gt mail peek                      # Preview first unread message
gt mail read <id|index>           # Read a message
gt mail send <address>            # Send a message
gt mail reply <id> [message]      # Reply to message
gt mail thread <id>               # View message thread
```

### Message Management
```bash
gt mail mark-read <id>            # Mark as read
gt mail mark-unread <id>          # Mark as unread
gt mail archive [id...]           # Archive messages
gt mail delete <id> [id...]       # Delete messages
gt mail clear [target]            # Clear all messages
gt mail search <query>            # Search by content
gt mail drain                     # Bulk-archive stale protocol messages
gt mail check                     # Check for new mail (for hooks)
gt mail directory                 # List valid recipient addresses
gt mail hook <msg-id>             # Attach mail to your hook
gt mail announces [channel]       # Show announcements
```

### Mail Queues
```bash
gt mail queue list                # List all queues
gt mail queue create <name>       # Create queue
gt mail queue show <name>         # Show queue details
gt mail queue delete <name>       # Delete queue
gt mail claim [queue-name]        # Claim message from queue
gt mail release <id>              # Release claimed message
```

### Mail Groups
```bash
gt mail group list                # List groups
gt mail group show <name>         # Show group details
gt mail group create <name>       # Create group
gt mail group add <group> <addr>  # Add member
gt mail group remove <group> <addr> # Remove member
gt mail group delete <name>       # Delete group
```

### Mail Channels
```bash
gt mail channel list              # List channels
gt mail channel show <name>       # Show channel messages
gt mail channel create <name>     # Create channel
gt mail channel delete <name>     # Delete channel
gt mail channel subscribe <name>  # Subscribe
gt mail channel unsubscribe <name> # Unsubscribe
gt mail channel subscribers <name> # List subscribers
```

### Address Format
- **Individual**: `rig/role` (e.g., "gastown/Toast", "mayor/")
- **Crew**: `rig/crew/name` (e.g., "gastown/crew/max")
- **Human**: `--human` flag
- **Mailing lists**: `list:name`
- **Queues**: `queue:name`
- **Announce**: `announce:channel`

### Delivery Modes
- **queue**: Stored in mailbox, agent checks with `gt mail check`
- **interrupt**: Injected directly into agent's session

### Message Types
task, escalation, scavenge, notification, reply

### Priority Levels
low, normal, high, urgent

## nudge — Synchronous message to worker

```bash
gt nudge <session> "message"
```

## broadcast — Send to all workers

```bash
gt broadcast "message"
```

## escalate — Escalation system

Severity-based routing for critical issues.

```bash
gt escalate "description"                 # Create escalation (default: medium)
gt escalate "desc" --severity high        # With severity (critical/high/medium/low)
gt escalate "desc" --reason "details"     # With detailed reason
gt escalate "desc" --source "plugin:x"    # With source identifier
gt escalate list                          # List open escalations
gt escalate show <id>                     # Show details
gt escalate ack <id>                      # Acknowledge
gt escalate close <id> --reason "fixed"   # Close resolved
gt escalate stale                         # Re-escalate stale unacknowledged
```

Flags: `-s, --severity`, `-r, --reason`, `--source`, `--related`, `--stdin`, `-n, --dry-run`, `--json`

## peek — View session output

```bash
gt peek <session>                 # View recent output from polecat or crew
```

## dnd — Do Not Disturb

```bash
gt dnd                            # Toggle DND mode
```

## notify — Notification level

```bash
gt notify <level>                 # Set notification level
```
