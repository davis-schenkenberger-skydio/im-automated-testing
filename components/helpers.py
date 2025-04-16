import re

from playwright.sync_api import Locator


def get_rotate(element: Locator):
    style = element.get_attribute("style")

    search = re.search(r"rotate\(([-\d.]+)deg\)", style)

    return int(search.group(1))
