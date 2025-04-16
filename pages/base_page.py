from abc import ABC, abstractmethod

from playwright.sync_api import Page


class BasePage(ABC):
    @abstractmethod
    def __init__(self, page: Page):
        self.page = page

    @abstractmethod
    def goto(self):
        raise NotImplementedError
