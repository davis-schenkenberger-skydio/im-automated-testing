def check_change(func):
    class ChangeCheck:
        def __init__(self, func, after_func=None, change_func=lambda b, a: a - b):
            self.func = func
            self.change_func = change_func
            self.after_func = after_func or func

        def __enter__(self):
            self.before = func()

        def __exit__(self, *_):
            self.after = self.after_func()
            self.change = self.change_func(self.before, self.after)

    return ChangeCheck(func)
