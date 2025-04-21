import contextlib
import re
from collections import namedtuple
from functools import wraps

from components.dropdown import Dropdown
from components.map import Map
from components.slider import Slider
from components.tab_list import TabList
from playwright.sync_api import Locator, Page

from .base_page import BasePage
from .rfd_page import RFD


class Missions(BasePage):
    def __init__(self, page):
        super().__init__(page)

        self.create = page.get_by_role("button", name="Create New Mission")

    def goto(self):
        self.page.goto("missions")

    def create_map_capture(self):
        self.create.click()
        self.page.get_by_label("Create New Mission").get_by_text("Map Capture").click()
        self.page.get_by_role("button", name="Next").click()
        self.page.wait_for_load_state()

        return MissionEditor(self.page)


class MissionsLibrary(Missions):
    def __init__(self, page):
        super().__init__(page)

        self.select_dock_e = Dropdown(
            self.page.locator("//*[contains(@class, 'OnlineVehicleSelector')]")
        )
        self.modal = self.page.locator(".ant-modal-content")
        self.run_e = self.modal.get_by_role("button", name="Run Mission")

    def goto(self):
        self.page.goto("missions/library")

    def missions(self):
        return [LibraryMission(e) for e in self.page.get_by_test_id("list-container").all()]

    def mission(self, name: str):
        return LibraryMission(
            self.page.locator(
                f"//*[@data-testid='list-container'][.//*[text()='{name}']]"
            )
        )

    def run_mission(self, mission, dock: str):
        if isinstance(mission, str):
            mission = self.mission(mission)

        mission.run()
        self.select_dock(dock)
        self.run_e.click()

        return RFD(self.page)

    def select_dock(self, dock: str):
        self.select_dock_e.select(re.compile(f".*{dock}.*"))


class LibraryMission:
    def __init__(self, element: Locator):
        self.element = element
        self.page = element.page
        self.run_e = self.element.get_by_role("button", name=" Run Mission")
        self.options = self.element.locator("//*[contains(@id, 'radix')]")

    def run(self):
        self.run_e.click()

    def delete(self):
        self.options.click()
        self.page.locator("span", has_text="Delete").click()
        self.page.get_by_role("button", name="Delete").click()


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
        v = self.color_gsd_e.text_content()
        amount, unit = v.split(" ")

        return float(amount)

    def thermal_gsd(self):
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

    def param_change(self):
        return ParamChange(self)

    def _wait_for_loading(self, expected=False):
        loading = self.page.locator(".ant-skeleton-button").first
        if expected:
            with contextlib.suppress(Exception):
                loading.wait_for(state="visible", timeout=10000)

        loading.wait_for(state="detached")
        
        # just make sure that the values are updated
        self.page.wait_for_timeout(1500)

    def goto(self):
        self.page.goto("missions/editor/3d-scan/unsaved")

    def search_in_map(self, query: str):
        self.map_search.press_sequentially(query, delay=200)
        self.map_search.press("Enter")


class ParamChange:
    def __init__(self, instance):
        self.instance = instance

    def __enter__(self):
        self.instance._wait_for_loading()
        self.before_photos = self.instance.photos()
        self.before_time = self.instance.time()
        self.before_color_gsd = self.instance.color_gsd()
        self.before_thermal_gsd = self.instance.thermal_gsd()

        return self

    def __exit__(self, *_):
        self.instance._wait_for_loading(expected=True)
        self.after_photos = self.instance.photos()
        self.after_time = self.instance.time()
        self.after_color_gsd = self.instance.color_gsd()
        self.after_thermal_gsd = self.instance.thermal_gsd()

    def change(self, attribute):
        before = getattr(self, f"before_{attribute}")
        after = getattr(self, f"after_{attribute}")
        return after - before


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
        self.flight_dir = Slider(self._get_selector("Flight Direction", "div"))

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
        return self.modal.locator(f"//span[normalize-space(.)='{text}']/parent::div")

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
