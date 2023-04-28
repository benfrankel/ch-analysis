import os.path

import cache
from . import const


STATE_FILEPATH = os.path.join(const.BASE_DIRPATH, 'state.json')


def load():
    manager = Manager()
    manager.load()
    return manager


class Manager:
    def __init__(self):
        # Local cache
        self.state_cache = cache.Cache(
            STATE_FILEPATH,
            format=cache.Format.JSON,
        )

        # In-memory storage
        self.state = {}

        # Flags
        self.is_loaded = False

    def _reload_state(self):
        self.state_cache.reload()
        self.state = self.state_cache.data
        self.state.setdefault('admins', [])
        self.state.setdefault('accounts', {})
        self.state.setdefault('account_add_attempts', {})
        self.state.setdefault('account_add_attempts_start', {})
        self.state.setdefault('account_add_attempts_reset', {})
        self.state.setdefault('wishlists', {})
        self.state.setdefault('parties', {})
    
    def load(self):
        if self.is_loaded:
            return

        self._reload_state()
    
        self.is_loaded = True

    def reload(self):
        self.is_loaded = False
        self.load()

    def save(self):
        if not self.is_loaded:
            return

        self.state_cache.save()

    @property
    def admins(self):
        return self.state['admins']

    @property
    def accounts(self):
        return self.state['accounts']

    @property
    def account_add_attempts(self):
        return self.state['account_add_attempts']

    @property
    def account_add_attempts_start(self):
        return self.state['account_add_attempts_start']

    @property
    def account_add_attempts_reset(self):
        return self.state['account_add_attempts_reset']

    @property
    def wishlists(self):
        return self.state['wishlists']

    @property
    def parties(self):
        return self.state['parties']
