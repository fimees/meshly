from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass
class Config:

    host: str = "0.0.0.0"
    port: int = 1488

    database: str = "meshly.db"

    certificate: str = "server.crt"
    private_key: str = "server.key"

    max_message_length: int = 2000
    history_limit: int = 50


def load_config(
    path: str = "config.toml",
) -> Config:

    config_path = Path(path)

    if not config_path.exists():
        return Config()

    with config_path.open("rb") as file:
        data = tomllib.load(file)

    server = data.get("server", {})
    security = data.get("security", {})

    return Config(
        host=server.get(
            "host",
            "0.0.0.0",
        ),

        port=server.get(
            "port",
            1488,
        ),

        database=server.get(
            "database",
            "meshly.db",
        ),

        certificate=security.get(
            "certificate",
            "server.crt",
        ),

        private_key=security.get(
            "private_key",
            "server.key",
        ),

        max_message_length=server.get(
            "max_message_length",
            2000,
        ),

        history_limit=server.get(
            "history_limit",
            50,
        ),
    )
