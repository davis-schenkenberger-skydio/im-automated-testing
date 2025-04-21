from datetime import datetime

import pytest

import data.config as cfg
from pages.missions_page import MissionEditor, MissionsLibrary


@pytest.fixture(scope="session")
def mission_name():
    return f"Test Mission {datetime.now()}"


@pytest.mark.manual
def test_create_mission(mission: MissionEditor, mission_name):
    mission.mission_details.open()

    mission.mission_details.name.fill(mission_name)
    mission.map.drag_bounds_to_coords(mission.page.mouse, cfg.SCAN_CORNERS)

    mission.scan_settings.open()

    mission.scan_settings.height.fill_box("200")
    mission.scan_settings.overlap.fill_box("80")
    mission.scan_settings.sidelap.fill_box("80")
    mission.scan_settings.crosshatch.click()
    mission.scan_settings.max_speed.fill_box("20")

    mission.set_return.open()

    mission.save.click()

    library = MissionsLibrary(mission.page)

    rfd = library.run_mission(mission_name, cfg.DOCK_NAME)
    rfd.launch.click(timeout=120000)
    rfd.fly_again.wait_for(timeout=0)
