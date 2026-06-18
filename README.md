<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=36&duration=3500&pause=800&color=00FFAA&center=true&vCenter=true&width=600&height=80&lines=fwdsh+%F0%9F%94%93+Forward+Shell;Interactive+shell+via+RCE;No+reverse+shell+needed;Just+forward+execution" alt="fwdsh Typing Animation" />
</p>

<p align="center">
  <b>⚡ Get an interactive shell using only an RCE vulnerability — no reverse shell, no listener, no hassle.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.6%2B-00FFAA?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Platform-Linux-FF6B6B?style=for-the-badge&logo=linux&logoColor=white" />
  <img src="https://img.shields.io/badge/Purpose-Pentesting-FFD700?style=for-the-badge&logo=kalilinux&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-7B68EE?style=for-the-badge" />
</p>

---

## 🔍 What is fwdsh?

**fwdsh** (Forward Shell) is a Python-based tool that turns a simple **RCE (Remote Code Execution)** vulnerability into a fully interactive shell — without needing a reverse connection, bind shell, or any outbound firewall bypass.

Traditional reverse shells require the target to connect back to you. fwdsh works **forward**: you send commands through the existing RCE vector and read output over HTTP.

---

## 🧠 How It Works

fwdsh consists of **two components** that work together:

### 📡 1. `rce_server.py` — The Target Listener

This script runs on the **target server**. It starts a lightweight HTTP server that:

- Listens for incoming GET requests with a `?cmd=` parameter
- Decodes the **Base64-encoded** command
- Executes it via `bash -c` using `subprocess.run()`
- Returns the command output in the HTTP response

```bash
python3 rce_server.py              # default port 54321
python3 rce_server.py 9999         # custom port
```

### 🖥️ 2. `fshell.py` — The Attacker Client

This script runs on **your machine**. It:

1. Checks that the RCE endpoint is reachable and working
2. Creates a **named pipe** (`mkfifo`) on the target at `/tmp/in.<SESSION_ID>`
3. Starts a background process on the target: `tail -f /tmp/in.<ID> | bash -i > /tmp/out.<ID>`
4. Opens an interactive prompt where every command you type is sent into the pipe
5. A parallel thread continuously reads the output file (`/tmp/out.<ID>`) and displays it in real-time

```bash
python3 fshell.py http://target:54321/rce.php?cmd=%s
```

### 📝 توضیحات فارسی

**fwdsh** یک ابزار forward shell است که با استفاده از RCE (اجرای کد از راه دور) یک شل تعاملی به شما می‌دهد — بدون نیاز به reverse shell.
فقط کافیست `rce_server.py` روی سرور قربانی اجرا شود و شما با `fshell.py` به آن متصل شوید. تمام دستورات از طریق HTTP ارسال شده و خروجی دریافت می‌شود.

> استفاده از این ابزار برای مقاصد مخرب غیرقانونی است. مسئولیت استفاده با خودتان می‌باشد.

---

## 📂 Project Structure

```
fwdsh/
├── rce_server.py    # HTTP server on target — executes base64 commands
├── fshell.py        # Client on your machine — interactive shell over RCE
├── setup.sh         # One-command setup & deployment script
└── README.md
```

---

## 🚀 Usage

### Prerequisites

| Component | Requirements |
|-----------|-------------|
| **Target** | Python 3 (any version) |
| **Attacker** | Python 3 + `requests` + `termcolor` |

```bash
pip install requests termcolor
```

### Step 1 — Deploy on Target

Upload `rce_server.py` to the target (via your RCE, file upload, wget, etc.) and run:

```bash
python3 rce_server.py
```

### Step 2 — Connect from Your Machine

```bash
python3 fshell.py http://target-ip:54321/rce.php?cmd=%s
```

### Shell Commands

| Command | Description |
|---------|-------------|
| `upgrade_shell` | Spawn a full TTY with PTY, TERM, and aliases |
| `get_sessid` | Show current session ID |
| `exit_shell` | Gracefully exit and clean up temp files |
| `help_shell` | Show available commands |

### ⚙️ setup.sh

The included `setup.sh` script automates deployment:

```bash
bash setup.sh
```

It clones (or pulls) the repo into `~/.fwdsh` and starts `rce_server.py` in the background on port 54321.

---

## ⚠️ Disclaimer

> **This tool is provided for educational purposes and authorized security testing only.**
>
> Using fwdsh against systems without explicit permission is **illegal** and **unethical**. You are solely responsible for complying with all applicable laws.
>
> The author assumes **no liability** for any misuse or damage caused by this project. **Use at your own risk.**

---

## 📜 License

MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=18&duration=4000&pause=500&color=00FFAA&center=true&vCenter=true&width=500&lines=%E2%AD%90+If+you+find+this+useful%2C+drop+a+star!;%F0%9F%94%92+Forward+Shell+%7C+No+reverse+connection+needed;%F0%9F%9B%A1+For+educational+use+only" alt="Footer Banner" />
</p>

<p align="center">
  <a href="https://github.com/ixiflower/fwdsh">
    <img src="https://img.shields.io/github/stars/ixiflower/fwdsh?style=for-the-badge&logo=github&color=00FFAA" alt="GitHub Stars" />
  </a>
</p>
