import socket
import ssl
import threading

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from ..config import load_config
from ..protocol import (
    encode_message,
    decode_message,
)


class MeshlyApp(App):

    CSS = """
    Screen {
        layout: vertical;
    }

    #main {
        height: 1fr;
    }

    #chat {
        width: 1fr;
        border: round cyan;
        padding: 1;
    }

    #sidebar {
        width: 28;
        border: round blue;
        padding: 1;
    }

    #messages {
        height: 1fr;
        overflow-y: auto;
    }

    #input {
        dock: bottom;
        margin-top: 1;
    }

    #room {
        text-style: bold;
        color: cyan;
        height: 3;
    }

    .message {
        margin-bottom: 1;
    }

    .system {
        color: gray;
    }

    .private {
        color: magenta;
    }

    .online {
        color: green;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
    ]

    def __init__(
        self,
        host="127.0.0.1",
        port=1488,
    ):

        super().__init__()

        self.host = host
        self.port = port

        self.client = None

        self.username = ""
        self.room = "general"

    def compose(self) -> ComposeResult:

        yield Header(
            show_clock=True
        )

        with Horizontal(id="main"):

            with Vertical(id="chat"):

                yield Label(
                    "# general",
                    id="room",
                )

                yield ListView(
                    id="messages"
                )

                yield Input(
                    placeholder=(
                        "Write a message..."
                    ),
                    id="input",
                )

            with Vertical(id="sidebar"):

                yield Static(
                    "[bold cyan]ONLINE[/bold cyan]"
                )

                yield ListView(
                    id="users"
                )

                yield Static(
                    "\n[bold blue]ROOMS[/bold blue]"
                )

                yield ListView(
                    id="rooms"
                )

        yield Footer()

    def on_mount(self):

        self.connect()

    def connect(self):

        raw = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        context = (
            ssl.create_default_context()
        )

        # Self-signed development certificate.
        context.check_hostname = False
        context.verify_mode = (
            ssl.CERT_NONE
        )

        self.client = (
            context.wrap_socket(
                raw,
                server_hostname="Meshly",
            )
        )

        self.client.connect(
            (
                self.host,
                self.port,
            )
        )

        thread = threading.Thread(
            target=self.receive_loop,
            daemon=True,
        )

        thread.start()

        self.login_screen()

    def login_screen(self):

        self.notify(
            "Connecté to Meshly",
            severity="information",
        )

        username = self.query_one(
            "#input",
            Input,
        )

        username.placeholder = (
            "Enter /login or /register..."
        )

    def receive_loop(self):

        buffer = b""

        while True:

            try:

                data = self.client.recv(
                    4096
                )

                if not data:
                    break

                buffer += data

                while b"\n" in buffer:

                    raw, buffer = (
                        buffer.split(
                            b"\n",
                            1,
                        )
                    )

                    if not raw:
                        continue

                    message = decode_message(
                        raw
                    )

                    self.call_from_thread(
                        self.handle_message,
                        message,
                    )

            except Exception as error:

                self.call_from_thread(
                    self.notify,
                    f"Connection error: {error}",
                    severity="error",
                )

                break

    def send(self, data):

        try:

            self.client.send(
                encode_message(data)
            )

        except OSError:

            self.notify(
                "Connection lost",
                severity="error",
            )

    def handle_message(
        self,
        message,
    ):

        message_type = message.get(
            "type"
        )

        if message_type == "auth_required":

            self.notify(
                "Use: /login username password",
                severity="information",
            )

        elif message_type == "auth_success":

            self.username = message.get(
                "username",
                self.username,
            )

            self.notify(
                message.get(
                    "text",
                    "Logged in",
                ),
                severity="information",
            )

            self.send(
                {
                    "type": "users"
                }
            )

            self.send(
                {
                    "type": "rooms"
                }
            )

        elif message_type == "auth_failed":

            self.notify(
                message["text"],
                severity="error",
            )

        elif message_type == "message":

            self.add_message(
                message["username"],
                message["text"],
            )

        elif message_type == "private_message":

            username = message[
                "username"
            ]

            text = message[
                "text"
            ]

            if message.get(
                "self",
                False,
            ):

                self.add_private(
                    f"→ {username}",
                    text,
                )

            else:

                self.add_private(
                    f"← {username}",
                    text,
                )

        elif message_type == "system":

            self.add_system(
                message["text"]
            )

        elif message_type == "error":

            self.notify(
                message["text"],
                severity="error",
            )

        elif message_type == "history":

            self.room = message[
                "room"
            ]

            self.query_one(
                "#room",
                Label,
            ).update(
                f"# {self.room}"
            )

            self.query_one(
                "#messages",
                ListView,
            ).clear()

            for (
                username,
                text,
                timestamp,
            ) in message[
                "messages"
            ]:

                self.add_message(
                    username,
                    text,
                    timestamp,
                )

        elif message_type == "room_joined":

            self.room = message[
                "room"
            ]

            self.query_one(
                "#room",
                Label,
            ).update(
                f"# {self.room}"
            )

        elif message_type == "users":

            self.update_users(
                message["users"]
            )

        elif message_type == "rooms":

            self.update_rooms(
                message["rooms"]
            )

        elif message_type == "help":

            self.add_system(
                "/users   online users\n"
                "/rooms   rooms\n"
                "/join X  join room\n"
                "/msg X Y private message\n"
                "/status X change status\n"
                "/quit    exit"
            )

    def add_message(
        self,
        username,
        text,
        timestamp=None,
    ):

        if timestamp:
            timestamp = timestamp[
                11:16
            ]

        else:
            timestamp = ""

        label = Static(
            f"[bold cyan]{username}[/bold cyan] "
            f"[dim]{timestamp}[/dim]\n"
            f"{text}",
            classes="message",
        )

        self.query_one(
            "#messages",
            ListView,
        ).append(
            ListItem(label)
        )

    def add_system(
        self,
        text,
    ):

        label = Static(
            f"[dim cyan]● {text}[/dim cyan]",
            classes="system",
        )

        self.query_one(
            "#messages",
            ListView,
        ).append(
            ListItem(label)
        )

    def add_private(
        self,
        username,
        text,
    ):

        label = Static(
            f"[bold magenta]{username}[/bold magenta]\n"
            f"{text}",
            classes="private",
        )

        self.query_one(
            "#messages",
            ListView,
        ).append(
            ListItem(label)
        )

    def update_users(
        self,
        users,
    ):

        view = self.query_one(
            "#users",
            ListView,
        )

        view.clear()

        for user in users:

            view.append(
                ListItem(
                    Label(
                        f"● {user}",
                        classes="online",
                    )
                )
            )

    def update_rooms(
        self,
        rooms,
    ):

        view = self.query_one(
            "#rooms",
            ListView,
        )

        view.clear()

        for room in rooms:

            view.append(
                ListItem(
                    Label(
                        f"# {room}"
                    )
                )
            )

    def on_input_submitted(
        self,
        event: Input.Submitted,
    ):

        text = event.value.strip()

        event.input.value = ""

        if not text:
            return

        # LOGIN

        if text.startswith(
            "/login "
        ):

            parts = text.split(
                " ",
                2,
            )

            if len(parts) != 3:

                self.notify(
                    "/login username password",
                    severity="error",
                )

                return

            self.send(
                {
                    "action": "login",
                    "username": parts[1],
                    "password": parts[2],
                }
            )

            return

        # REGISTER

        if text.startswith(
            "/register "
        ):

            parts = text.split(
                " ",
                2,
            )

            if len(parts) != 3:

                self.notify(
                    "/register username password",
                    severity="error",
                )

                return

            self.send(
                {
                    "action": "register",
                    "username": parts[1],
                    "password": parts[2],
                }
            )

            return

        # ROOMS

        if text == "/rooms":

            self.send(
                {
                    "type": "rooms"
                }
            )

            return

        # USERS

        if text == "/users":

            self.send(
                {
                    "type": "users"
                }
            )

            return

        # JOIN

        if text.startswith(
            "/join "
        ):

            room = text.split(
                " ",
                1,
            )[1]

            self.send(
                {
                    "type": "join",
                    "room": room,
                }
            )

            return

        # PRIVATE

        if text.startswith(
            "/msg "
        ):

            parts = text.split(
                " ",
                2,
            )

            if len(parts) < 3:

                self.notify(
                    "/msg username message",
                    severity="error",
                )

                return

            self.send(
                {
                    "type": "private_message",
                    "target": parts[1],
                    "text": parts[2],
                }
            )

            return

        # STATUS

        if text.startswith(
            "/status "
        ):

            status = text.split(
                " ",
                1,
            )[1]

            self.send(
                {
                    "type": "status",
                    "status": status,
                }
            )

            return

        # HELP

        if text == "/help":

            self.send(
                {
                    "type": "help"
                }
            )

            return

        # QUIT

        if text == "/quit":

            self.send(
                {
                    "type": "quit"
                }
            )

            self.exit()

            return

        # NORMAL MESSAGE

        self.send(
            {
                "type": "message",
                "text": text,
            }
        )


def main():

    config = load_config()

    app = MeshlyApp(
        host="127.0.0.1",
        port=config.port,
    )

    app.run()


if __name__ == "__main__":
    main()
