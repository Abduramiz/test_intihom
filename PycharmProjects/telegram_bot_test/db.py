import json
import os

FAYL = "test.json"


def yukla():
    try:
        with open(FAYL, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def saqla(users):
    with open(FAYL, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def user_saqla(chat_id, ism, javoblar=None):
    users = yukla()
    users[str(chat_id)] = {
        "ism": ism,
        "javoblar": javoblar or [],
        "natija": sum(javoblar or [])
    }
    saqla(users)


def user_ol(chat_id):
    return yukla().get(str(chat_id))


def jami():
    return len(yukla())


def user_ochir(chat_id):
    users = yukla()
    users.pop(str(chat_id), None)
    saqla(users)
