from collections import namedtuple
from functools import wraps

from components.dropdown import Dropdown
from components.slider import Slider
from components.tab_list import TabList
from playwright.sync_api import Locator, Page
from utils.map import Map

from .base_page import BasePage


class Missions(BasePage):
    def __init__(self, page):
        super().__init__(page)

        self.create = page.get_by_role("button", name="Create New Mission")

    def goto(self):
        self.page.goto("missions")

    def create_map_capture(self):
        self.create.click()
        self.page.get_by_text("Map Capture").click()
        self.page.get_by_role("button", name="Next").click()
        self.page.wait_for_load_state()

        return MissionEditor(self.page)


class MissionsLibrary(Missions):
    def __init__(self, page):
        super().__init__(page)

    def goto(self):
        self.page.goto("missions/library")


class MissionsSchedule(Missions):
    def __init__(self, page):
        super().__init__(page)

    def goto(self):
        self.page.goto("missions/schedule")


class MissionsRuns(Missions):
    def __init__(self, page):
        super().__init__(page)

    def goto(self):
        self.page.goto("missions/runs")


class MissionEditor(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page.wait_for_load_state("domcontentloaded")

        self.map = Map(page)
        self.map_search = self.page.get_by_role("textbox", name="search")

        accordion_form = self.page.locator(".AccordionForm_mid__reais > div > div")
        self.mission_details = MissionDetails(accordion_form.nth(0))
        self.scan_settings = ScanSettings(accordion_form.nth(1))
        self.set_return = ReturnBehavior(accordion_form.nth(2))
        self.review_json = ReviewJson(accordion_form.nth(3))

        self.discard = self.page.get_by_role("button", name="Discard")
        self.save = self.page.get_by_role("button", name="Save Mission Plan")
        self.table = self.page.locator("table").last
        self.time_e = self.table.locator("td").nth(0)
        self.photos_e = self.table.locator("td").nth(1)
        self.color_gsd_e = self.table.locator("td").nth(2)
        self.thermal_gsd_e = self.table.locator("td").nth(3)

    def color_gsd(self):
        self._check_loading()

        v = self.color_gsd_e.text_content()
        amount, unit = v.split(" ")

        return float(amount)

    def thermal_gsd(self):
        self._check_loading()

        v = self.thermal_gsd_e.text_content()
        amount, unit = v.split(" ")

        return float(amount)

    def time(self):
        v = self.time_e.text_content()

        if "Too large" in v:
            return float("inf")

        if v.startswith(">"):
            v = v.lstrip("> ")

        time, unit = v.split(" ")

        if unit == "min":
            return float(time)

        if unit == "hr":
            return float(time) * 60

        raise ValueError(f"Unknown time unit: {unit}")

    def photos(self):
        v = self.photos_e.text_content()

        if v == "-":
            return float("inf")

        return float(v)

    def _wait_for_change(self, func, attempts=200):
        start = func()
        for _ in range(attempts):
            self.page.wait_for_timeout(200)
            new = func()
            if new != start:
                return new

        return start

    def wait_for_photos(self):
        return self._wait_for_change(self.photos)

    def wait_for_time(self):
        return self._wait_for_change(self.time)

    def wait_for_color_gsd(self):
        return self._wait_for_change(self.color_gsd)

    def wait_for_thermal_gsd(self):
        return self._wait_for_change(self.thermal_gsd)

    def goto(self):
        self.page.goto("missions/editor/3d-scan/unsaved")

    def search_in_map(self, query: str):
        self.map_search.press_sequentially(query, delay=200)
        self.map_search.press("Enter")


class EditorAccordion:
    def __init__(self, element: Locator):
        self.element = element
        self.heading = self.element.locator(".AccordionForm_sectionHeading__yykmm")

    def open(self):
        if not self.is_open():
            self.heading.click()

    def close(self):
        if self.is_open():
            self.heading.click()

    def is_open(self):
        return self.heading.locator(".anticon-down").is_visible(timeout=1000)


class MissionDetails(EditorAccordion):
    def __init__(self, element: Locator):
        super().__init__(element)

        self.name = self._get_selector("Name", "input")
        self.site = Dropdown(self._get_selector("Site", "div"))
        self.dock = Dropdown(self._get_selector("Dock", "div"))
        self.add_boundary = self.element.get_by_role(
            "button", name="Add Outer Boundary"
        )

    def _get_selector(self, label: str, tag: str) -> Locator:
        return self.element.locator(
            f"//span[text()='{label}']/parent::div/following-sibling::{tag}"
        ).first


class ScanSettings(EditorAccordion):
    def __init__(self, element: Locator):
        super().__init__(element)

        self.height = Slider(self._get_selector("Height above Launch Point", "div"))
        self.gimbal_angle = Slider(self._get_selector("Gimbal Angle", "div"))
        self.overlap = Slider(self._get_selector("Overlap", "div"))
        self.sidelap = Slider(self._get_selector("Sidelap", "div"))
        self.crosshatch = self._get_selector("Crosshatch", "button")
        self.perimeter = self._get_selector("Perimeter", "button")
        self.perimeter_overlap = Slider(self._get_selector("Overlap", "div", nth=1))
        self.perimeter_angle = Slider(
            self._get_selector("Perimeter Gimbal Angle", "div")
        )
        self.stop_for_photo = self._get_selector("Stop for Photo", "button")
        self.strict_boundaries = self._get_selector("Strict Boundaries", "button")
        self.max_speed = Slider(self._get_selector("Maximum Speed", "div"))
        self.custom_flight_dir = self._get_selector("Custom Flight Direction", "button")
        self.perpendicular_heading = self._get_selector(
            "Use Perpendicular Heading", "button"
        )
        self.camera_settings = CameraSettings(self._get_camera_settings_selector())

    def _get_selector(self, label: str, tag: str, nth=0) -> Locator:
        return self.element.locator(
            f"//span[text()='{label}']/parent::div/following-sibling::{tag}[1]"
        ).nth(nth)

    def _get_camera_settings_selector(self) -> Locator:
        return self.element.locator("button", has_text="Edit")


class ReturnBehavior(EditorAccordion): ...


class ReviewJson(EditorAccordion): ...


@staticmethod
def _open_tab(tab_button):
    def decorator(func):
        @wraps(func)
        def wrapper(self):
            self.open()
            getattr(self, tab_button).click()
            return func(self)

        return wrapper

    return decorator


class CameraSettings:
    CaptureSetting = namedtuple("CaptureSetting", ["slider", "input", "auto_on"])

    def __init__(self, element: Locator):
        self.element = element
        self.page = self.element.page
        self.modal = self.page.locator("//*[contains(@class, 'CameraActionEditor')]")
        self.settings = self.page.locator("[id^='rc-tabs-'][id$='-tab-Settings']")
        self.capture = self.page.locator("[id^='rc-tabs-'][id$='-tab-Capture']")

    def is_open(self):
        return self.modal.is_visible(timeout=0)

    def close(self):
        self.modal.locator("button", name="Close").click()

    def open(self):
        if not self.is_open():
            self.element.click()

    def _sensor_menu_selector(self):
        return self.modal.locator(
            "//span[normalize-space(.)='Estimates for:']/following-sibling::button"
        ).first

    def select_sensor(self, sensor: str):
        self._sensor_menu_selector().click()
        self.page.locator("span", has_text=rf"{sensor}").click()

    def _tablist_selector(self, text: str):
        # following-sibling::div//
        return self.modal.locator(
            f"//span[normalize-space(.)='{text}']/parent::div"
        ).firstZeroDivisionError

    def _capture_setting(self, name: str):
        row = self.modal.locator(
            f"//*[contains(@class, 'exposureCompRow') and"
            f".//text()[contains(., '{name}')]]"
        )

        return self.CaptureSetting(
            slider=Slider(row),
            input=row.locator("input").first,
            auto_on=row.locator("button", has_text="Auto On").first,
        )

    @staticmethod
    def _make_tablist_property(label):
        @property
        @_open_tab("settings")
        def tablist(self):
            return TabList(self._tablist_selector(label))

        return tablist

    @staticmethod
    def _make_capture_property(label):
        @property
        @_open_tab("capture")
        def capture_setting(self):
            return self._capture_setting(label)

        return capture_setting

    resolution = _make_tablist_property("Resolution")
    camera_mode = _make_tablist_property("Camera Mode")
    camera_sensor = _make_tablist_property("Camera Sensor")
    image_file_type = _make_tablist_property("Image File Type")
    capture_thermal = _make_tablist_property("Capture Thermal")
    thermal_file_type = _make_tablist_property("Thermal File Type")

    white_balance = _make_capture_property("White Balance")
    shutter_speed = _make_capture_property("Shutter Speed")
    iso = _make_capture_property("ISO")
    brightness = _make_capture_property("Brightness (EV)")
