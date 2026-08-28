# 🔐 Meshly

### Secure • Lightweight • Terminal-based LAN Messenger

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux-lightgrey?logo=linux)
![Status](https://img.shields.io/badge/Status-Development-orange)

**Meshly** is a terminal-based LAN messenger written in Python.

It allows multiple users to communicate through a local network or a virtual LAN using TCP sockets and TLS encryption.

> ⚠️ Meshly is currently an educational/hobby project and is still under development.

---

## 🖥️ Preview

![Meshly Terminal Interface](./docs/screenshot.png)

---

# ✨ Features

* 🔐 TLS encrypted connections
* 👤 User registration and authentication
* 🔑 Password hashing
* 💬 Real-time messaging
* 🏠 Chat rooms
* 💌 Private messages
* 👥 Online users
* 🟢 User statuses
* 💾 SQLite database
* 🖥️ Terminal user interface
* 🌐 LAN support
* 🔌 TCP socket networking
* ⚙️ Configurable server
* 📝 Server logging

---

# 🛠️ Tech Stack

| Technology   | Purpose                |
| ------------ | ---------------------- |
| Python 3.11+ | Core language          |
| TCP sockets  | Network communication  |
| TLS / SSL    | Encrypted connections  |
| SQLite       | Database               |
| JSON         | Communication protocol |
| Textual      | Terminal UI            |
| Threading    | Multiple clients       |

---

# 📁 Project Structure

```text
meshly/
│
├── .gitignore
├── LICENSE
├── README.md
├── config.example.toml
├── flake.nix
├── pyproject.toml
│
├── docs/
│   └── screenshot.png
│
├── src/
│   └── meshly/
│       ├── __init__.py
│       ├── auth.py
│       ├── client.py
│       ├── config.py
│       ├── database.py
│       ├── protocol.py
│       ├── server.py
│       │
│       └── ui/
│           ├── __init__.py
│           └── app.py
│
└── tests/
```

---

# 🚀 Installation

## Requirements

Before installing Meshly, make sure you have:

* Python **3.11 or newer**
* OpenSSL
* Git
* A Linux/macOS environment or another Unix-like system

Check Python:

```bash
python3 --version
```

Example:

```text
Python 3.13.5
```

Check OpenSSL:

```bash
openssl version
```

Check Git:

```bash
git --version
```

---

# 📥 1. Clone the repository

Clone Meshly from GitHub:

```bash
git clone https://github.com/fimees/meshly.git
```

Enter the project directory:

```bash
cd meshly
```

---

# 🐍 2. Create a virtual environment

Creating a virtual environment keeps Meshly's Python dependencies isolated from the rest of your system.

Run:

```bash
python3 -m venv .venv
```

Activate it:

### Linux / macOS

```bash
source .venv/bin/activate
```

After activation, your terminal should look similar to:

```text
(.venv) user@computer:~/meshly$
```

---

# 📦 3. Install Meshly

Install the project and its dependencies:

```bash
pip install -e .
```

The `-e` option installs Meshly in editable mode.

This is useful during development because changes to the source code are immediately available without reinstalling the package.

You can verify the installation:

```bash
meshly --help
```

and:

```bash
meshly-server --help
```

---

# ⚙️ Configuration

Meshly uses a TOML configuration file.

Create your local configuration from the example:

```bash
cp config.example.toml config.toml
```

Open it:

```bash
nano config.toml
```

or:

```bash
code config.toml
```

Example configuration:

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

### Configuration options

#### `[server]`

`host`

```toml
host = "0.0.0.0"
```

Determines which network interfaces the server listens on.

`0.0.0.0` means that the server accepts connections through available network interfaces.

---

`port`

```toml
port = 1488
```

The TCP port used by Meshly.

The default port is:

```text
1488
```

---

`database`

```toml
database = "meshly.db"
```

SQLite database used to store Meshly data.

---

`max_message_length`

```toml
max_message_length = 2000
```

Maximum allowed message length.

---

`history_limit`

```toml
history_limit = 50
```

Number of previous messages loaded for chat history.

---

# 🔐 TLS Certificate

Meshly uses TLS to encrypt communication between clients and the server.

For local development, you can generate a self-signed certificate.

## Generate the private key

```bash
openssl genrsa -out server.key 2048
```

## Generate the certificate

```bash
openssl req -new -x509 \
    -key server.key \
    -out server.crt \
    -days 365 \
    -subj "/CN=Meshly"
```

Check that both files exist:

```bash
ls -l server.key server.crt
```

You should see:

```text
server.crt
server.key
```

### ⚠️ Security warning

`server.key` is a **private key**.

Never upload it to GitHub.

The same applies to:

```text
server.crt
config.toml
meshly.db
```

The repository should only contain:

```text
config.example.toml
```

---

# ▶️ Running the Server

Make sure your virtual environment is active:

```bash
source .venv/bin/activate
```

Start the server:

```bash
meshly-server
```

If everything is configured correctly, you should see something similar to:

```text
Meshly server started
Listening on 0.0.0.0:1488
TLS enabled
```

Keep this terminal open.

The server must remain running while clients are connected.

---

# 💬 Running the Client

Open another terminal.

Go to the Meshly directory:

```bash
cd meshly
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Start the client:

```bash
meshly
```

The terminal interface should open.

You can now connect to the Meshly server.

---

# 👥 Multiple Clients

You can run multiple Meshly clients simultaneously.

For example:

```text
Terminal 1
└── meshly-server

Terminal 2
└── meshly

Terminal 3
└── meshly

Terminal 4
└── meshly
```

All clients can connect to the same server.

---

# 🌐 Using Meshly over LAN

Meshly can be used between computers connected to the same local network.

Find the server's local IP address.

On Linux:

```bash
ip addr
```

or:

```bash
hostname -I
```

Example:

```text
192.168.1.42
```

The client should connect to:

```text
192.168.1.42:1488
```

The server must be listening on:

```text
0.0.0.0:1488
```

Make sure your firewall allows TCP traffic on port `1488`.

---

# 🌍 Using a Virtual LAN

Meshly can also work through a virtual LAN.

For example, you can use software that creates a virtual network between computers.

The important part is that the client can reach the server's virtual IP address.

Example:

```text
Server
Virtual IP: 26.x.x.x
Port:       1488

Client
       │
       │ Virtual LAN
       ▼
Server: 26.x.x.x:1488
```

The exact virtual network software is not required by Meshly.

Meshly only needs TCP connectivity between the client and server.

---

# 🏠 Chat Rooms

Meshly supports multiple chat rooms.

Example:

```text
/rooms
```

Possible output:

```text
#general
#gaming
#development
```

Join a room:

```text
/join gaming
```

---

# 💬 Commands

Meshly provides terminal commands for interacting with the server.

### Authentication

```text
/register <username> <password>
```

Create a new account.

```text
/login <username> <password>
```

Log into an existing account.

---

### Rooms

```text
/rooms
```

Display available rooms.

```text
/join <room>
```

Join a room.

Example:

```text
/join general
```

---

### Users

```text
/users
```

Show currently online users.

---

### Private messages

```text
/msg <username> <message>
```

Example:

```text
/msg alex Hello!
```

---

### Status

```text
/status online
```

```text
/status away
```

```text
/status busy
```

---

### Help

```text
/help
```

Display available commands.

---

### Exit

```text
/quit
```

Close the client.

---

# 🗄️ Database

Meshly uses SQLite.

The database is created locally:

```text
meshly.db
```

It can contain information such as:

* user accounts
* password hashes
* rooms
* messages
* chat history

The database is intentionally excluded from Git.

---

# 🔒 Security

Meshly currently provides:

* TLS encrypted connections
* Password hashing
* Authentication
* Input validation
* Message length limits

However, Meshly is **not currently intended for production or public Internet deployment**.

The development setup uses a self-signed TLS certificate.

Certificate verification and other security improvements are planned for future versions.

---

# 🧪 Development

Install the project in editable mode:

```bash
pip install -e .
```

Run the server:

```bash
meshly-server
```

Run the client:

```bash
meshly
```

---

# 🧪 Tests

Tests are located in:

```text
tests/
```

Run them with:

```bash
pytest
```

If pytest is not installed:

```bash
pip install pytest
```

---

# ❄️ NixOS

Meshly also contains a `flake.nix`.

On NixOS, enter the development environment with:

```bash
nix develop
```

Then install Meshly:

```bash
pip install -e .
```

You can then run:

```bash
meshly-server
```

and:

```bash
meshly
```

---

# 🐛 Troubleshooting

## `ModuleNotFoundError`

Example:

```text
ModuleNotFoundError: No module named 'textual'
```

Make sure your virtual environment is active:

```bash
source .venv/bin/activate
```

Then reinstall:

```bash
pip install -e .
```

---

## `FileNotFoundError: server.crt`

If you see:

```text
FileNotFoundError: [Errno 2] No such file or directory
```

at:

```text
context.load_cert_chain(...)
```

generate the TLS certificate again:

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

## `Address already in use`

If you see:

```text
OSError: [Errno 98] Address already in use
```

another process is already using port `1488`.

Check it:

```bash
ss -ltnp | grep :1488
```

Stop the old Meshly server or change the port in `config.toml`.

---

## `Connection refused`

Make sure:

1. `meshly-server` is running.
2. The client is using the correct server IP.
3. The port is `1488`.
4. The firewall allows TCP traffic.
5. Both computers can reach each other.

Test the connection:

```bash
nc -vz SERVER_IP 1488
```

---

# 🗺️ Roadmap

## v0.1

* [x] TCP server
* [x] Multiple clients
* [x] Authentication
* [x] Password hashing
* [x] TLS
* [x] Public chat
* [x] Private messages
* [x] Chat rooms
* [x] SQLite database
* [x] Terminal UI

## Future

* [ ] Better TLS certificate verification
* [ ] Improved authentication UI
* [ ] Message timestamps
* [ ] User profiles
* [ ] File transfer
* [ ] Image sharing
* [ ] Emoji reactions
* [ ] Mentions
* [ ] Message editing
* [ ] Message deletion
* [ ] Server administration
* [ ] Automated tests
* [ ] End-to-end encryption
* [ ] Better NixOS integration
* [ ] Windows support
* [ ] macOS support

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a branch:

```bash
git checkout -b feature/my-feature
```

3. Make your changes.
4. Test the project.
5. Commit:

```bash
git commit -m "Add my feature"
```

6. Push your branch:

```bash
git push origin feature/my-feature
```

7. Open a Pull Request.

---

# 📜 License

Meshly is licensed under the MIT License.

See [`LICENSE`](./LICENSE.md) for details.

---

# ⭐ Support

If you like Meshly, consider giving the project a ⭐ on GitHub.

Issues, suggestions and pull requests are welcome.

---

**Meshly — simple communication, built from scratch.**
