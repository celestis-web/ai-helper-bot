from collections import defaultdict, deque

# user_id -> deque of {"role": "user"/"assistant", "content": str}
MAX_HISTORY = 10

_history = defaultdict(lambda: deque(maxlen=MAX_HISTORY))


def add_message(user_id: int, role: str, content: str):
    _history[user_id].append({"role": role, "content": content})


def get_history(user_id: int) -> list:
    return list(_history[user_id])


def clear_history(user_id: int):
    _history[user_id].clear()