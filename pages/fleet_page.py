from .base_page import BasePage


class Fleet(BasePage):
    def __init__(self, page):
        super().__init__(page)

    def goto(self):
        self.page.goto("fleet")
