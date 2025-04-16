from playwright.sync_api import Locator


class Slider:
    def __init__(self, element: Locator):
        self.element = element
        self.rail = self.element.locator(".ant-slider-rail")
        self.handle = self.element.locator(".ant-slider-handle")
        self.input = self.element.locator("input")

    def slide(self, percentage: float):
        width = self.rail.bounding_box()["width"]
        click_position = max(0, min(width * percentage, width))

        # use a negative offset to make sure we get all the way to the end
        if click_position == 0:
            click_position = -10

        rail_position = self.rail.bounding_box()
        handle_position = self.handle.bounding_box()

        self.rail.page.mouse.move(x=handle_position["x"], y=handle_position["y"])
        self.rail.page.mouse.down()
        self.rail.page.wait_for_timeout(100)
        self.rail.page.mouse.move(
            rail_position["x"] + click_position, rail_position["y"]
        )
        self.rail.page.mouse.up()
        self.rail.page.wait_for_timeout(500)

    def fill_box(self, value: str):
        self.input.fill(str(value))
        self.input.press("Enter")
        self.input.page.locator("body").click()
        self.input.page.wait_for_timeout(1000)  # TODO: FLAKY

    def get_value(self):
        return self.input.input_value()
