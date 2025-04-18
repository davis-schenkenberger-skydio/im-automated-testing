from .base_page import BasePage


class RFD(BasePage):
    def __init__(self, page):
        super().__init__(page)

        self.skill_set = page.get_by_test_id("skillSelector")
        self.exit = page.get_by_test_id("rfd-exit-button")
        self.distance = page.get_by_test_id("telemetry-distance-from-launch")
        self.gimbal_pitch = page.get_by_test_id("telemetry-gimbal-pitch")
        self.fly_again = page.get_by_role("button", name="Fly Again")
        self.launch = page.get_by_role("button", name="Launch")
