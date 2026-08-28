import json


def encode_message(data: dict) -> bytes:
    return (
        json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def decode_message(data: bytes) -> dict:
    return json.loads(data.decode("utf-8"))
