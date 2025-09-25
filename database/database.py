from typing import Dict, Any


def db_init() -> Dict[str, Dict[str, set[Any]]]:
    return {
        "user_template": {
            "page": 1,
            "bookmarks": set(),
        },
        "users": {},
    }
