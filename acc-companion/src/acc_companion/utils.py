from functools import wraps


class AlreadyBlocksError(Exception):
    pass


class Guard:
    def __init__(self):
        self.blocks = False

    def __enter__(self):
        self.block()

    def __exit__(self, exc_type, exc_value, traceback):
        self.unblock()

    def block(self):
        if self.blocks:
            raise AlreadyBlocksError()
        self.blocks = True

    def unblock(self):
        self.blocks = False

    @classmethod
    def block_recursion(cls, func):
        guard = cls()

        @wraps(func)
        def wrapper(*args, **kwargs):
            if not guard.blocks:
                with guard:
                    return func(*args, **kwargs)

        return wrapper
