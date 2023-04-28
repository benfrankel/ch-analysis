from . import state


class Context:
    def __init__(self):
        self.state = state.State()

    def load(self):
        self.state.load()
