import re

import pytest
from pytest import FixtureRequest as Request

import data.config as cfg
from pages.missions_page import MissionEditor, Missions
from playwright.sync_api import Page


@pytest.fixture
def open_mission_from_cloud(auth_page: Page):
    mission_page = Missions(auth_page)
    mission_page.goto()

    mission = mission_page.create_map_capture()
    auth_page.wait_for_load_state()
    return mission


@pytest.fixture
def mission_editor(auth_page: Page):
    mission_editor = MissionEditor(auth_page)
    mission_editor.goto()

    auth_page.wait_for_load_state()
    return mission_editor


@pytest.fixture
def name(request: Request):
    name = getattr(request, "param", None)

    return name


@pytest.fixture
def site(request: Request):
    site = getattr(request, "param", cfg.SITE_NAME)

    return site


@pytest.fixture
def dock(request: Request):
    dock = getattr(request, "param", cfg.DOCK_NAME)

    return dock


@pytest.fixture
def boundary(request: Request):
    boundary = getattr(request, "param", True)

    return boundary


@pytest.fixture
def mission(mission_editor: MissionEditor, name, site, dock, boundary):
    if dock and (site is None):
        pytest.skip("Cannot run test with no site but a dock")

    if name:
        mission_editor.mission_details.name.fill(name)

    if site:
        mission_editor.mission_details.site.select(site)

    if dock:
        mission_editor.mission_details.dock.select(re.compile(dock + ".*"))

    if boundary:
        with mission_editor.map.poll_for_map_change():
            mission_editor.mission_details.add_boundary.click()

        mission_editor.map.drag_bounds_to_coords(
            mission_editor.page.mouse, cfg.SCAN_CORNERS
        )

    return mission_editor
