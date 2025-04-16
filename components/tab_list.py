import re

from playwright.sync_api import Locator


class TabList:
    def __init__(self, element: Locator):
        self.element = element
        self.page = element.page
        self.tablist = element.locator("//div[@data-slot='tabList']")
        self.notice = element.locator("span").last
        self.title = element.locator("span").first
        self.warning_button = element.locator("svg")
        self.warning_content = self.page.locator(
            "//div[@data-slot='content' and @data-open='true']"
        ).last

        self.page = element.page
        self.buttons = element.locator("button")

    def selected(self) -> str:
        return self.tablist.locator("button[aria-selected=true]").text_content()

    def select(self, name: str):
        if self.selected() == name:
            return

        self.buttons.get_by_text(re.compile(f"{name}.*")).click()

    def disabled(self) -> bool:
        return self.buttons.first.is_disabled()
