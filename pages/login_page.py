from .base_page import BasePage


class Login(BasePage):
    def __init__(self, page):
        super().__init__(page)

        self.email = page.get_by_placeholder("Email")
        self.code = page.get_by_placeholder("Enter Code")
        self.continue_button = page.get_by_role("button", name="Continue")

    def goto(self):
        self.page.goto("login")

    def fill(self, cloud_email: str, code: str | None):
        self.email.fill(cloud_email)

        if code:
            self.code.fill(code)

        self.continue_button.click()
