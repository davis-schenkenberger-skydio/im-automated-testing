import re

import pytest

import data.config as cfg
import data.test_cases as tc
from components.helpers import get_rotate
from pages.missions_page import MissionEditor
from playwright.sync_api import expect
from utils.funcs import check_change
from utils.points import find_perpendicular_point, midpoint, sort_by_angle


@pytest.mark.testrail(id=[805497])
def test_open_editor(open_mission_from_cloud: MissionEditor):
    detail_e = open_mission_from_cloud.mission_details.element

    expect(detail_e, tc.TEST_805497).to_be_visible()


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[813391])
def test_map_search(mission: MissionEditor):
    mission.map.poll_for_map_ref()
    change = mission.map.map_change()

    with change:
        mission.search_in_map(cfg.ADDRESS_QUERY)
        mission.map.wait_for_not_zooming()

    assert change.bounds_changed
    assert mission.map.contains_location(cfg.ADDRESS_LOCATION)


@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[812324])
def test_add_boundaries(mission: MissionEditor):
    mission.map.poll_for_map_ref()
    mission.mission_details.open()

    boundary_button = mission.mission_details.add_boundary

    change = mission.map.map_change()

    with change:
        boundary_button.click()

    assert change.rendered > 0


@pytest.mark.parametrize("dock", [None], ids=["no dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=None)
def test_cant_add_boundaries(mission: MissionEditor):
    mission.mission_details.open()

    expect(mission.mission_details.add_boundary).to_be_disabled()


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[812325, 813402])
def test_skip_add_boundary(mission: MissionEditor):
    scan_settings = mission.scan_settings
    scan_settings.open()

    expect(scan_settings.element, tc.TEST_812325).to_contain_text(
        "Return to Step 1 to set an outer boundary"
    )


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[805426, 813395, 813391])
def test_mission_name(mission: MissionEditor):
    expect(mission.mission_details.name, tc.TEST_805425).to_have_attribute(
        "placeholder",
        cfg.DEFAULT_MISSION_NAME_RE,
        timeout=20000,  # long time out cause this can be flakey
    )

    mission.mission_details.name.fill(cfg.MISSION_NAME)

    mission.page.wait_for_timeout(
        500
    )  # TODO: find better way to give it time to save name

    mission.scan_settings.open()
    mission.mission_details.open()

    expect(mission.mission_details.name, tc.TEST_805426).to_have_value(cfg.MISSION_NAME)


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[813397, 813396])
def test_select_site(mission: MissionEditor):
    assert mission.mission_details.site.selected() == "No Site", tc.TEST_813396

    mission.mission_details.site.select(cfg.SITE_NAME)

    assert mission.mission_details.site.selected() == cfg.SITE_NAME, tc.TEST_813397


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[813398, 813401])
def test_site_selection_with_boundary(mission: MissionEditor):
    mission.mission_details.site.select(cfg.SITE_NAME)
    mission.mission_details.dock.select(re.compile(cfg.DOCK_NAME + ".*"))

    assert mission.mission_details.site.selected() == cfg.SITE_NAME, tc.TEST_813398
    assert cfg.DOCK_NAME in mission.mission_details.dock.selected(), tc.TEST_813401

    mission.mission_details.add_boundary.click()

    expect(mission.mission_details.site.input, tc.TEST_813398).to_be_disabled()
    expect(mission.mission_details.dock.input, tc.TEST_813401).to_be_disabled()


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[813400, 813392])
def test_site_selection_map(mission: MissionEditor):
    mission.map.poll_for_map_ref()
    change = mission.map.map_change()

    with change:
        mission.mission_details.site.select(cfg.SITE_NAME)

    assert change.bounds_changed, tc.TEST_813400
    assert change.rendered_changed > 0, tc.TEST_813392


@pytest.mark.parametrize("site", [None], ids=["no-site"], indirect=True)
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[813399])
def test_site_proceed_no_site(mission: MissionEditor):
    mission.search_in_map(cfg.ADDRESS_QUERY)
    mission.map.wait_for_not_zooming()

    mission.mission_details.add_boundary.click()

    mission.scan_settings.open()

    drag_map_ele = mission.scan_settings.element.get_by_text(
        "Drag the pillars on map to set your boundaries"
    )

    expect(drag_map_ele, tc.TEST_813399).to_be_visible()


@pytest.mark.parametrize("site", [cfg.SITE_NAME], ids=["site"])
@pytest.mark.parametrize("dock", [None], ids=["no-dock"], indirect=True)
@pytest.mark.parametrize("boundary", [False], ids=["no-boundary"], indirect=True)
@pytest.mark.testrail(id=[813000])
def test_dock_selection_map(mission: MissionEditor):
    change = mission.map.map_change()

    with change:
        mission.mission_details.dock.select(re.compile(cfg.DOCK_NAME + ".*"))

    # TODO: Better way of verifying that dock is showing in correct location
    assert change.rendered_changed > 0, tc.TEST_813000


@pytest.mark.testrail(id=[805428, 813394])
def test_boundary_edit(mission: MissionEditor):
    expect(mission.mission_details.add_boundary, tc.TEST_813394).to_be_hidden()

    before_moving = mission.map.get_current_map_points()

    mission.map.drag_bounds_to_coords(mission.page.mouse, cfg.SCAN_CORNERS)

    after_moving = mission.map.get_current_map_points()

    assert before_moving != after_moving, tc.TEST_805428


@pytest.mark.testrail(id=[805429])
def test_boundary_add(mission: MissionEditor):
    points = sort_by_angle(mission.map.get_current_map_points())
    a, b = points[1], points[2]

    mp = midpoint(a, b)
    goal = find_perpendicular_point(a, b)
    mpc = mission.map.correct_frame(mp)

    mission.page.mouse.move(**mpc, steps=10)
    mission.page.mouse.click(**mpc)

    mission.map.drag_point(mission.page.mouse, mp, goal, steps=10)

    assert len(points) < len(mission.map.get_current_map_points()), tc.TEST_805429


@pytest.mark.testrail(id=[805430, 805431])
def test_boundary_delete(mission: MissionEditor):
    points = mission.map.get_current_map_points()
    points = [mission.map.correct_frame(x) for x in points]
    points_iter = iter(points)

    first_point = next(points_iter)

    mission.page.mouse.click(**first_point)

    mission.page.press("body", "Delete")

    assert len(points) > len(mission.map.get_current_map_points())

    for point in points_iter:
        mission.page.mouse.click(**point)
        mission.page.press("body", "Delete")

        assert len(mission.map.get_current_map_points()) == 3


@pytest.mark.testrail(id=[805476, 805477, 812332, 812330, 805478])
def test_height_input(mission: MissionEditor):
    mission.scan_settings.open()
    height_slider = mission.scan_settings.height

    assert height_slider.get_value() == "66", tc.TEST_805476

    height_slider.slide(0)
    assert height_slider.get_value() == "3", tc.TEST_805477
    low_alt_time, low_alt_photos = mission.time(), mission.photos()

    height_slider.slide(1)
    assert height_slider.get_value() == "400", tc.TEST_805477
    high_alt_time, high_alt_photos = mission.time(), mission.photos()

    height_slider.fill_box(-100)
    assert height_slider.get_value() == "3", tc.TEST_812330

    height_slider.fill_box(500)
    assert height_slider.get_value() == "400", tc.TEST_812330

    height_slider.fill_box(5.123942)
    assert "." not in height_slider.get_value(), tc.TEST_812332

    assert high_alt_time < low_alt_time, tc.TEST_805478
    assert high_alt_photos < low_alt_photos, tc.TEST_805478


@pytest.mark.testrail(id=[813632, 812328, 812331, 812329, 813404])
def test_gimbal_angle_input(mission: MissionEditor):
    mission.scan_settings.open()
    gimbal_slider = mission.scan_settings.gimbal_angle
    camera = gimbal_slider.element.locator("img")

    assert gimbal_slider.get_value() == "90", tc.TEST_813632

    gimbal_slider.slide(0)
    assert gimbal_slider.get_value() == "55", tc.TEST_812328
    low_rotate = get_rotate(camera)

    gimbal_slider.slide(1)
    assert gimbal_slider.get_value() == "90", tc.TEST_812328
    high_rotate = get_rotate(camera)

    gimbal_slider.fill_box(-100)
    assert gimbal_slider.get_value() == "55", tc.TEST_812329

    gimbal_slider.fill_box(500)
    assert gimbal_slider.get_value() == "90", tc.TEST_812329

    gimbal_slider.fill_box(60.123942)
    assert "." not in gimbal_slider.get_value(), tc.TEST_812331

    assert high_rotate > low_rotate, tc.TEST_813404


@pytest.mark.testrail(id=[805480, 813405, 805481, 805483, 805484])
def test_sidelap_overlap(mission: MissionEditor):
    mission.scan_settings.open()

    overlap = mission.scan_settings.overlap
    sidelap = mission.scan_settings.sidelap

    assert overlap.get_value() == "70", tc.TEST_805480
    assert sidelap.get_value() == "70", tc.TEST_813405

    overlap.slide(0)
    sidelap.slide(0)

    assert overlap.get_value() == "1", tc.TEST_805481
    assert sidelap.get_value() == "1", tc.TEST_805483

    overlap.slide(1)
    sidelap.slide(1)

    assert overlap.get_value() == "95", tc.TEST_805481
    assert sidelap.get_value() == "95", tc.TEST_805483

    overlap.fill_box("0")
    sidelap.fill_box("0")

    photo_change = check_change(mission.photos)
    time_change = check_change(mission.time)
    with photo_change, time_change:
        overlap.fill_box("70")

    assert photo_change.change > 0, tc.TEST_805482
    assert time_change.change == 0, tc.TEST_805482

    with photo_change, time_change:
        sidelap.fill_box("70")

    assert photo_change.change > 0, tc.TEST_805484
    assert time_change.change > 0, tc.TEST_805484


@pytest.mark.testrail(id=[805457, 805461, 805462])
def test_crosshatch(mission: MissionEditor):
    # TODO: find a way to verify that crosshatch is displayed on map
    mission.scan_settings.open()
    crosshatch = mission.scan_settings.crosshatch
    photo_change = check_change(mission.photos)
    time_change = check_change(mission.time)
    map_change = mission.map.map_change()

    expect(crosshatch, tc.TEST_805457).to_be_checked(checked=False)

    with photo_change, time_change, map_change:
        crosshatch.click()
        expect(crosshatch).to_be_checked()

    assert photo_change.change > 0, tc.TEST_805461
    # assert map_change.rendered_changed > 0, tc.TEST_812333

    test_gimbal_angle_input(mission)

    with photo_change, time_change, map_change:
        crosshatch.click()
        expect(crosshatch).to_be_checked(checked=False)

    assert photo_change.change < 0, tc.TEST_812350
    assert time_change.change < 0, tc.TEST_812350
    # assert map_change.rendered_changed < 0, tc.TEST_812350


@pytest.mark.testrail(
    id=[
        812341,
        812335,
        813183,
        813185,
        813405,
        813184,
        813192,
        813406,
        813410,
        813417,
        813416,
        813414,
        813415,
    ]
)
def test_camera_settings(mission: MissionEditor):
    mission.scan_settings.open()

    camera_settings = mission.scan_settings.camera_settings
    camera_settings.open()

    expect(camera_settings.modal, tc.TEST_812341).to_be_visible()
    expect(camera_settings.resolution.element, tc.TEST_812335).to_be_visible()
    expect(camera_settings.camera_mode.element, tc.TEST_812335).to_be_visible()
    expect(camera_settings.camera_sensor.element, tc.TEST_812335).to_be_visible()
    expect(camera_settings.image_file_type.element, tc.TEST_812335).to_be_visible()
    expect(camera_settings.capture_thermal.element, tc.TEST_812335).to_be_visible()
    expect(camera_settings.thermal_file_type.element, tc.TEST_812335).to_be_visible()

    assert camera_settings.resolution.selected() == "Full", tc.TEST_813183
    assert camera_settings.camera_mode.disabled(), tc.TEST_813185
    expect(camera_settings.camera_mode.notice, tc.TEST_813405).to_contain_text(
        "only available in 1/4"
    )

    camera_settings.resolution.select("1/4")
    assert not camera_settings.camera_mode.disabled(), tc.TEST_813184

    gsd_change = check_change(mission.color_gsd)
    photos_change = check_change(mission.photos)

    camera_settings.camera_sensor.select("X10 Wide")
    with gsd_change, photos_change:
        camera_settings.camera_sensor.select("X10 Narrow")

    assert gsd_change.change < 0, tc.TEST_813192
    assert photos_change.change > 0, tc.TEST_813192

    assert camera_settings.image_file_type.selected() == "JPG", tc.TEST_813406

    assert camera_settings.capture_thermal.selected() == "Off", tc.TEST_813410
    assert camera_settings.thermal_file_type.disabled(), tc.TEST_813417

    camera_settings.capture_thermal.select("On")
    assert not camera_settings.thermal_file_type.disabled(), tc.TEST_813416

    assert camera_settings.thermal_file_type.selected() == "JPG", tc.TEST_813414
    camera_settings.thermal_file_type.select("RJPG")
    assert camera_settings.thermal_file_type.selected() == "RJPG", tc.TEST_813415


@pytest.mark.testrail(id=[813419, 813420, 813422, 813423])
def test_sensor_compatibility(mission: MissionEditor):
    mission.scan_settings.open()

    camera_settings = mission.scan_settings.camera_settings
    camera_settings.open()

    camera_settings.select_sensor("Skydio X10 VT300Z")
    camera_settings.camera_sensor.select("X10 Wide")

    camera_settings.camera_sensor.warning_button.hover()
    expect(
        camera_settings.camera_sensor.warning_content, tc.TEST_813419
    ).to_contain_text("Setting not available")

    camera_settings.camera_sensor.select("X10 Narrow")
    expect(camera_settings.camera_sensor.warning_button, tc.TEST_813420).to_be_hidden()

    camera_settings.select_sensor("Skydio X10 V100L")
    camera_settings.capture_thermal.select("On")

    camera_settings.capture_thermal.warning_button.hover()
    expect(
        camera_settings.capture_thermal.warning_content, tc.TEST_813422
    ).to_contain_text("Setting not available")

    camera_settings.thermal_file_type.warning_button.hover()
    expect(
        camera_settings.thermal_file_type.warning_content, tc.TEST_813422
    ).to_contain_text("Setting not available")

    camera_settings.capture_thermal.select("Off")
    expect(
        camera_settings.capture_thermal.warning_button, tc.TEST_813423
    ).to_be_hidden()
    expect(
        camera_settings.thermal_file_type.warning_button, tc.TEST_813423
    ).to_be_hidden()


@pytest.mark.testrail(
    id=[805440, 805441, 805442, 805443, 805444, 805445, 805446, 805447]
)
def test_perimeter_settings(mission: MissionEditor):
    mission.scan_settings.open()

    perimeter_toggle = mission.scan_settings.perimeter
    overlap = mission.scan_settings.perimeter_overlap
    angle = mission.scan_settings.perimeter_angle

    photo_change = check_change(mission.photos)
    time_change = check_change(mission.time)

    expect(perimeter_toggle, tc.TEST_805440).to_be_checked(checked=False)

    with photo_change, time_change:
        perimeter_toggle.click()
        expect(perimeter_toggle).to_be_checked()

    assert photo_change.change > 0, tc.TEST_805441
    assert time_change.change > 0, tc.TEST_805441

    expect(overlap.element, tc.TEST_805442).to_be_visible()
    expect(angle.element, tc.TEST_805442).to_be_visible()

    assert overlap.get_value() == "80", tc.TEST_805443

    overlap.slide(0)
    assert overlap.get_value() == "1", tc.TEST_805444

    with photo_change:
        overlap.slide(1)

    assert overlap.get_value() == "95", tc.TEST_805444
    assert photo_change.change > 0, tc.TEST_805445

    assert angle.get_value() == "60", tc.TEST_805446

    angle.slide(0)
    assert angle.get_value() == "10", tc.TEST_805447

    angle.slide(1)
    assert angle.get_value() == "80", tc.TEST_805447


@pytest.mark.testrail(id=[805434, 805435])
def test_stop_for_photo(mission: MissionEditor):
    mission.scan_settings.open()

    stop_for_photo = mission.scan_settings.stop_for_photo
    photo_change = check_change(mission.photos)
    time_change = check_change(mission.time)

    expect(stop_for_photo, tc.TEST_805434).to_be_checked(checked=False)

    with photo_change, time_change:
        stop_for_photo.click()

    expect(stop_for_photo).to_be_checked()

    assert photo_change.change == 0, tc.TEST_805435
    assert time_change.change > 0, tc.TEST_805435


@pytest.mark.testrail(id=[805437])
def test_strict_boundaries(mission: MissionEditor):
    # TODO: is there a way to verify boundaries are strict?
    mission.scan_settings.open()

    strict_boundaries = mission.scan_settings.strict_boundaries

    expect(strict_boundaries, tc.TEST_805437).to_be_checked(checked=False)


@pytest.mark.testrail(id=[805450, 805451, 805452])
def test_max_speed(mission: MissionEditor):
    mission.scan_settings.open()
    time_change = check_change(mission.time)
    max_speed = mission.scan_settings.max_speed
    max_speed.element.scroll_into_view_if_needed()

    assert max_speed.get_value() == "11", tc.TEST_805450

    max_speed.slide(0)
    assert max_speed.get_value() == "1", tc.TEST_805451

    with time_change:
        max_speed.slide(1)
        assert max_speed.get_value() == "36", tc.TEST_805451

    assert time_change.change < 0, tc.TEST_805452
