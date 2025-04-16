import re

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator
from utils.strings import matches


class Dropdown:
    def __init__(self, element: Locator):
        self.element = element
        self.page = element.page
        self.input = self.element.locator("input").first
        self.selector = self.element.locator(".ant-select-selector")
        self.options = self.page.locator(".ant-select-item-option")

    def selected(self):
        return self.selector.text_content()

    def select(self, option: str | re.Pattern, retry=5):
        if matches(self.selected(), option):
            return

        self.element.wait_for()
        self.element.click()
        # self.options.wait_for()

        try:
            self.options.get_by_text(option).first.click(timeout=1000)
        except PlaywrightError as e:
            if retry:
                return self.select(option, retry=retry - 1)

            raise e

    def visible(self) -> bool:
        return self.element.is_visible()
