import json

from . import const


is_loaded = False

state = {
    'wishlist': {},
}


def load():
    global is_loaded
    if is_loaded:
        return

    global state
    try:
        with open(const.PIZZATRON_STATE_FILEPATH, 'r') as f:
            state = json.load(f)
    except Exception:
        pass

    is_loaded = True


def save():
    if not is_loaded:
        return

    with open(const.PIZZATRON_STATE_FILEPATH, 'w') as f:
        json.dump(state, f)
