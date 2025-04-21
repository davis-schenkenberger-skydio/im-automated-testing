import contextlib
import re

from playwright.sync_api import Locator, expect
from utils.strings import matches


class Dropdown:
    def __init__(self, element: Locator):
        self.element = element
        self.page = element.page
        self.selector = self.element.locator(".ant-select-selector")
        self.input = self.selector.locator("input", has_not_text="").first
        self.options = self.page.locator(".ant-select-item-option")

    def selected(self) -> str:
        return self.selector.text_content().strip()

    def open(self):
        self.element.wait_for(state="visible", timeout=5000)
        self.selector.click(force=True)
        # expect(self.options.first).to_be_visible(timeout=5000)

    def close(self):
        if (
            self.input.is_visible()
            and self.element.get_attribute("aria-expanded") == "true"
        ):
            self.selector.click(force=True)

    def select(self, option: str | re.Pattern, retry: int = 10):
        for attempt in range(retry):
            try:
                if matches(self.selected(), option):
                    return

                with contextlib.suppress(AssertionError):
                    expect(self.input).to_be_enabled(timeout=10000)

                self.open()

                matched_option = self.options.get_by_text(option).first
                expect(matched_option).to_be_visible(timeout=3000)
                matched_option.click()

                if matches(self.selected(), option):
                    return

            except Exception as e:
                if attempt < retry:
                    self.close()
                    self.page.wait_for_timeout(300)  # short delay before retry
                    continue
                raise RuntimeError(f"Failed after {retry} attempts: {e}") from e

    def visible(self) -> bool:
        return self.element.is_visible()
