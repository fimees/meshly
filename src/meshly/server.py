import logging
import socket
import ssl
import threading

from .config import load_config
from .database import Database
from .protocol import (
    decode_message,
    encode_message,
)


config = load_config()
database = Database(config.database)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("meshly")


clients = {}

rooms = {
    "general": set(),
}

lock = threading.RLock()


def send(client, data):

    client.send(
        encode_message(data)
    )


def username_of(client):

    with lock:

        user = clients.get(client)

        if user is None:
            return None

        return user["username"]


def current_room(client):

    with lock:

        user = clients.get(client)

        if user is None:
            return None

        return user["room"]


def broadcast_room(
    room,
    data,
    exclude=None,
):

    with lock:

        targets = list(
            rooms.get(room, set())
        )

    for client in targets:

        if client == exclude:
            continue

        try:

            send(client, data)

        except OSError:

            remove_client(client)


def broadcast_all(
    data,
):

    with lock:

        targets = list(
            clients.keys()
        )

    for client in targets:

        try:

            send(client, data)

        except OSError:

            remove_client(client)


def online_users(room):

    with lock:

        return [
            info["username"]
            for info in clients.values()
            if info["room"] == room
        ]


def remove_client(client):

    with lock:

        info = clients.pop(
            client,
            None,
        )

        if info is None:
            return

        username = info["username"]
        room = info["room"]

        if room in rooms:
            rooms[room].discard(client)

    try:
        client.close()
    except OSError:
        pass

    logger.info(
        "%s disconnected",
        username,
    )

    broadcast_room(
        room,
        {
            "type": "system",
            "text": f"{username} left #{room}",
        },
    )


def validate_username(username):

    if not username:
        return False

    if len(username) > 32:
        return False

    return username.replace(
        "_",
        "",
    ).isalnum()


def validate_room(room):

    if not room:
        return False

    if len(room) > 32:
        return False

    return room.replace(
        "_",
        "",
    ).replace(
        "-",
        "",
    ).isalnum()


def authenticate(client):

    while True:

        send(
            client,
            {
                "type": "auth_required",
            },
        )

        data = client.recv(4096)

        if not data:
            return None

        raw = data.split(
            b"\n",
            1,
        )[0]

        message = decode_message(raw)

        action = message.get(
            "action"
        )

        username = str(
            message.get(
                "username",
                "",
            )
        ).strip()

        password = str(
            message.get(
                "password",
                "",
            )
        )

        if not validate_username(
            username
        ):

            send(
                client,
                {
                    "type": "auth_failed",
                    "text": "Invalid username",
                },
            )

            continue

        if len(password) > 256:

            send(
                client,
                {
                    "type": "auth_failed",
                    "text": "Password is too long",
                },
            )

            continue

        if action == "register":

            if database.register(
                username,
                password,
            ):

                send(
                    client,
                    {
                        "type": "auth_success",
                        "text": "Registration successful",
                    },
                )

            else:

                send(
                    client,
                    {
                        "type": "auth_failed",
                        "text": "Username already exists",
                    },
                )

        elif action == "login":

            if not database.login(
                username,
                password,
            ):

                send(
                    client,
                    {
                        "type": "auth_failed",
                        "text": "Invalid username or password",
                    },
                )

                continue

            with lock:

                already_online = any(
                    info["username"] == username
                    for info in clients.values()
                )

                if already_online:
                    pass
                else:

                    clients[client] = {
                        "username": username,
                        "room": "general",
                        "status": "online",
                    }

                    rooms[
                        "general"
                    ].add(client)

            if already_online:

                send(
                    client,
                    {
                        "type": "auth_failed",
                        "text": "User is already online",
                    },
                )

                continue

            send(
                client,
                {
                    "type": "auth_success",
                    "text": f"Welcome, {username}!",
                    "username": username,
                },
            )

            send_history(
                client,
                "general",
            )

            broadcast_room(
                "general",
                {
                    "type": "system",
                    "text": f"{username} joined #general",
                },
                exclude=client,
            )

            return username

        else:

            send(
                client,
                {
                    "type": "auth_failed",
                    "text": "Unknown action",
                },
            )


def send_history(
    client,
    room,
):

    history = database.history(
        room,
        config.history_limit,
    )

    send(
        client,
        {
            "type": "history",
            "room": room,
            "messages": history,
        },
    )


def handle_client(
    client,
    address,
):

    logger.info(
        "Connection from %s",
        address,
    )

    try:

        username = authenticate(
            client
        )

        if username is None:
            return

        buffer = b""

        while True:

            data = client.recv(4096)

            if not data:
                break

            buffer += data

            while b"\n" in buffer:

                raw, buffer = buffer.split(
                    b"\n",
                    1,
                )

                if not raw:
                    continue

                try:

                    message = decode_message(
                        raw
                    )

                except Exception:

                    send(
                        client,
                        {
                            "type": "error",
                            "text": "Invalid message",
                        },
                    )

                    continue

                message_type = message.get(
                    "type"
                )

                # -------------------------
                # PUBLIC MESSAGE
                # -------------------------

                if message_type == "message":

                    text = str(
                        message.get(
                            "text",
                            "",
                        )
                    ).strip()

                    if not text:
                        continue

                    if len(text) > config.max_message_length:

                        send(
                            client,
                            {
                                "type": "error",
                                "text": (
                                    "Message is too long"
                                ),
                            },
                        )

                        continue

                    room = current_room(
                        client
                    )

                    database.save_message(
                        username,
                        room,
                        text,
                    )

                    broadcast_room(
                        room,
                        {
                            "type": "message",
                            "username": username,
                            "room": room,
                            "text": text,
                        },
                    )

                # -------------------------
                # JOIN ROOM
                # -------------------------

                elif message_type == "join":

                    room = str(
                        message.get(
                            "room",
                            "",
                        )
                    ).strip().lower()

                    if not validate_room(
                        room
                    ):

                        send(
                            client,
                            {
                                "type": "error",
                                "text": "Invalid room name",
                            },
                        )

                        continue

                    with lock:

                        old_room = clients[
                            client
                        ]["room"]

                        if room not in rooms:
                            rooms[room] = set()

                        rooms[
                            old_room
                        ].discard(client)

                        rooms[
                            room
                        ].add(client)

                        clients[
                            client
                        ]["room"] = room

                    send(
                        client,
                        {
                            "type": "room_joined",
                            "room": room,
                        },
                    )

                    send_history(
                        client,
                        room,
                    )

                    broadcast_room(
                        room,
                        {
                            "type": "system",
                            "text": (
                                f"{username} "
                                f"joined #{room}"
                            ),
                        },
                        exclude=client,
                    )

                # -------------------------
                # ROOMS
                # -------------------------

                elif message_type == "rooms":

                    with lock:

                        room_list = sorted(
                            rooms.keys()
                        )

                    send(
                        client,
                        {
                            "type": "rooms",
                            "rooms": room_list,
                        },
                    )

                # -------------------------
                # USERS
                # -------------------------

                elif message_type == "users":

                    room = current_room(
                        client
                    )

                    send(
                        client,
                        {
                            "type": "users",
                            "room": room,
                            "users": online_users(room),
                        },
                    )

                # -------------------------
                # PRIVATE MESSAGE
                # -------------------------

                elif message_type == "private_message":

                    target = str(
                        message.get(
                            "target",
                            "",
                        )
                    ).strip()

                    text = str(
                        message.get(
                            "text",
                            "",
                        )
                    ).strip()

                    if not target or not text:
                        continue

                    if len(text) > config.max_message_length:

                        send(
                            client,
                            {
                                "type": "error",
                                "text": "Message is too long",
                            },
                        )

                        continue

                    target_client = None

                    with lock:

                        for c, info in clients.items():

                            if info["username"] == target:

                                target_client = c
                                break

                    if target_client is None:

                        send(
                            client,
                            {
                                "type": "error",
                                "text": (
                                    f"{target} is offline"
                                ),
                            },
                        )

                        continue

                    payload = {
                        "type": "private_message",
                        "username": username,
                        "text": text,
                    }

                    send(
                        target_client,
                        payload,
                    )

                    send(
                        client,
                        {
                            **payload,
                            "self": True,
                            "target": target,
                        },
                    )

                # -------------------------
                # STATUS
                # -------------------------

                elif message_type == "status":

                    status = str(
                        message.get(
                            "status",
                            "online",
                        )
                    )

                    allowed = {
                        "online",
                        "away",
                        "busy",
                    }

                    if status not in allowed:
                        continue

                    with lock:

                        clients[
                            client
                        ]["status"] = status

                    broadcast_all(
                        {
                            "type": "status",
                            "username": username,
                            "status": status,
                        },
                    )

                # -------------------------
                # HELP
                # -------------------------

                elif message_type == "help":

                    send(
                        client,
                        {
                            "type": "help",
                        },
                    )

                # -------------------------
                # QUIT
                # -------------------------

                elif message_type == "quit":

                    return

    except (
        ConnectionResetError,
        BrokenPipeError,
        OSError,
    ):

        pass

    except Exception:

        logger.exception(
            "Client error: %s",
            address,
        )

    finally:

        remove_client(client)


def create_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1,
    )

    server.bind(
        (
            config.host,
            config.port,
        )
    )

    server.listen(100)

    context = ssl.SSLContext(
        ssl.PROTOCOL_TLS_SERVER
    )

    context.load_cert_chain(
        config.certificate,
        config.private_key,
    )

    return server, context


def main():

    server, context = create_server()

    logger.info(
        "Meshly server started"
    )

    logger.info(
        "Listening on %s:%s",
        config.host,
        config.port,
    )

    logger.info(
        "TLS enabled"
    )

    try:

        while True:

            raw_client, address = (
                server.accept()
            )

            try:

                client = (
                    context.wrap_socket(
                        raw_client,
                        server_side=True,
                    )
                )

            except ssl.SSLError:

                raw_client.close()

                continue

            thread = threading.Thread(
                target=handle_client,
                args=(
                    client,
                    address,
                ),
                daemon=True,
            )

            thread.start()

    except KeyboardInterrupt:

        logger.info(
            "Server shutting down"
        )

    finally:

        server.close()


if __name__ == "__main__":
    main()
