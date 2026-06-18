# fwdsh - Forward Shell

Get an interactive shell using only an RCE vulnerability (no reverse shell needed).

## How it works

1. **`rce_server.py`** runs on the target — HTTP server that executes base64 commands.
2. **`fshell.py`** runs on your machine — connects to the RCE server, creates a named pipe on the target, and gives you an interactive shell.

## Usage

### 1. On the target server
```bash
python3 rce_server.py
# or with custom port: python3 rce_server.py 9999
```

### 2. On your machine
```bash
python3 fshell.py http://target-ip:54321/rce.php?cmd=%s
```

### Shell commands
| Command | Description |
|---------|-------------|
| `upgrade_shell` | Spawn a full TTY |
| `get_sessid` | Show session ID |
| `exit_shell` | Exit and clean up |

## Requirements

**Target:** Python 3  
**Attacker:** Python 3 + `requests` + `termcolor`
