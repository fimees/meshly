# 🔐 Meshly

### Secure • Lightweight • Terminal-based

**Meshly** is a terminal LAN messenger written in Python.

It allows users to communicate through a local network or a virtual LAN while providing authentication, encrypted connections, chat rooms and message history.

---

## ✨ Features

* 🔐 TLS encrypted connections
* 👤 User registration and authentication
* 🔑 Secure password hashing
* 💬 Real-time messaging
* 💌 Private messages
* 🏠 Dynamic chat rooms
* 💾 SQLite message history
* 👥 Online users
* 🟢 User statuses
* 🖥️ Terminal UI
* 🌐 LAN / virtual LAN support
* ⚙️ Configurable server
* 📝 Server logging

---

## 🖥️ Preview

> Add a screenshot or GIF of Meshly here.

```text
┌──────────────────────────────────────────────────────────────┐
│                         M E S H L Y                         │
├────────────────────────────────────────┬─────────────────────┤
│ # general                              │ ONLINE              │
│                                        │                     │
│ Alice                                  │ ● Alice             │
│ Hello!                                 │ ● Bob               │
│                                        │ ● Alex              │
│ Bob                                    │                     │
│ Hey!                                   │ ROOMS               │
│                                        │                     │
│                                        │ # general           │
│                                        │ # gaming            │
├────────────────────────────────────────┴─────────────────────┤
│ Write a message...                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology  | Purpose               |
| ----------- | --------------------- |
| Python      | Core language         |
| TCP sockets | Network communication |
| TLS         | Connection encryption |
| SQLite      | Message/user storage  |
| JSON        | Network protocol      |
| Textual     | Terminal UI           |
| Threading   | Concurrent clients    |

---

## 📁 Project Structure

```text
meshly/
├── src/
│   └── meshly/
│       ├── auth.py
│       ├── client.py
│       ├── config.py
│       ├── database.py
│       ├── protocol.py
│       ├── server.py
│       └── ui/
│           └── app.py
│
├── tests/
├── config.example.toml
├── flake.nix
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## 🚀 Installation

### Clone

```bash
git clone https://github.com/YOUR_USERNAME/meshly.git
cd meshly
```

### Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Meshly

```bash
pip install -e .
```

---

## 🔐 Generate a development certificate

Meshly currently uses a self-signed certificate for development.

```bash
openssl genrsa -out server.key 2048
```

```bash
openssl req -new -x509 \
    -key server.key \
    -out server.crt \
    -days 365 \
    -subj "/CN=Meshly"
```

---

## ⚙️ Configuration

Copy the example configuration:

```bash
cp config.example.toml config.toml
```

Example:

```toml
[server]
host = "0.0.0.0"
port = 1488
database = "meshly.db"
max_message_length = 2000
history_limit = 50

[security]
certificate = "server.crt"
private_key = "server.key"
```

---

## ▶️ Running

Start the server:

```bash
meshly-server
```

Then, in another terminal:

```bash
meshly
```

---

## 💬 Commands

```text
/login <username> <password>
/register <username> <password>

/rooms
/users
/join <room>

/msg <username> <message>

/status online
/status away
/status busy

/help
/quit
```

---

## 🌐 LAN / Virtual LAN

Meshly can be used over a local network or a virtual LAN.

The server listens on:

```text
0.0.0.0:1488
```

For example, when using a virtual network, configure the client to connect to the server's virtual IP address.

```python
HOST = "YOUR_SERVER_IP"
PORT = 1488
```

---

## 🗺️ Roadmap

### Meshly 1.0

* [x] TCP server
* [x] Multiple clients
* [x] Authentication
* [x] Password hashing
* [x] TLS
* [x] Public chat
* [x] Private messages
* [x] Chat rooms
* [x] SQLite history
* [x] Terminal UI

### Future

* [ ] Proper TLS certificate verification
* [ ] Better authentication UI
* [ ] Message timestamps in the UI
* [ ] User profiles
* [ ] File transfer
* [ ] Reactions
* [ ] Mentions
* [ ] Server administration
* [ ] Automated tests
* [ ] End-to-end encryption

---

## ⚠️ Security

Meshly is currently a hobby/educational project.

The development client uses a self-signed TLS certificate and does not currently perform full certificate verification.

Do not expose the current development configuration directly to the public Internet.

---

## 📜 License

Meshly is released under the MIT License.
