def check_change(func):
    class ChangeCheck:
        def __init__(self, func, change_func=lambda b, a: a - b):
            self.func = func
            self.change_func = change_func

        def __enter__(self):
            self.before = func()

        def __exit__(self, *_):
            self.after = func()
            self.change = self.change_func(self.before, self.after)

    return ChangeCheck(func)
