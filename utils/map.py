import time
from contextlib import contextmanager

from playwright.sync_api import Error as PlaywriteError
from playwright.sync_api import Page
from utils.points import pair_by_angle


class Map:
    def __init__(self, page: Page):
        self.page = page
        self.canvas = page.locator("canvas").first
        self.three_loaded = False

    @property
    def mapbox(self):
        return self._get_ref("mapboxMapRef")

    @property
    def threejs(self):
        return self._get_ref("threeStateRef")

    @property
    def handle(self):
        return self._get_store()

    def _get_store(self):
        for _ in range(10):
            try:
                return self.page.evaluate_handle(
                    "window.__DEV_GET_ZUSTAND_STORE_MAP().getState()"
                )
            except PlaywriteError:
                time.sleep(2)

        raise PlaywriteError("Failed to get map store")

    def _get_ref(self, ref: str):
        for _ in range(10):
            try:
                out = self.handle.evaluate_handle(f"handle => handle.{ref}.current")

                if out != "null":
                    return out
            except PlaywriteError:
                ...
            time.sleep(2)

        raise PlaywriteError(f"Failed to get ref {ref}")

    def wait_for_not_zooming(self):
        while self.is_zooming():
            time.sleep(0.2)

    def is_zooming(self):
        return self.page.evaluate("map => map.isZooming()", self.mapbox)

    def get_bounds(self):
        return self.page.evaluate("map => map.getBounds()", self.mapbox)

    def contains_location(self, location: tuple[float, float]) -> bool:
        location = f"lat: {location[0]}, lon: {location[1]}"
        location = "{" + location + "}"
        return self.page.evaluate(
            f"map => map.getBounds().contains({location})", self.mapbox
        )

    def project_lat_lng(self, location: tuple[float, float]):
        return self.page.evaluate(
            f"map => map.project([{location[0]}, {location[1]}])", self.mapbox
        )

    def convert_scan_to_px(self, scan: list[list[float]]):
        out = []

        for point in scan:
            out.append(self.project_lat_lng(point))

        return out

    def get_rendered_object_count(self):
        elements = self.page.evaluate(
            "three => three.internal.interaction", self.threejs
        )

        return len(elements)

    def poll_for_map_ref(self, attempts=50):
        for _ in range(attempts):
            try:
                self.get_bounds()
                return True
            except PlaywriteError:
                time.sleep(0.2)

        return False

    def get_current_map_points(self):
        if not self.three_loaded:
            self.load_three_js()
            self.three_loaded = True

        script = """three => {
            const sprites = three.internal.interaction.filter(element => element.name === "EditableVertexSprite");
            const camera = three.camera;
            const renderer = three.gl;

            const screenPositions = [];

            sprites.forEach(sprite => {
                const worldPosition = new THREE.Vector3();
                sprite.getWorldPosition(worldPosition);
                const ndc = worldPosition.clone().project(camera);
                const widthHalf = renderer.domElement.width / 2;
                const heightHalf = renderer.domElement.height / 2;
                const screenX = (ndc.x * widthHalf) + widthHalf;
                const screenY = -(ndc.y * heightHalf) + heightHalf;

                screenPositions.push({ x: screenX, y: screenY });
            });

            console.log(screenPositions);

            return screenPositions;
        }"""  # noqa: E501

        return self.page.evaluate(script, self.threejs)

    def load_three_js(self):
        script = """() => {
            const src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
            return new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = src;
                script.onload = () => {
                console.log(`${src} loaded`);
                resolve();
                };
                script.onerror = () => {
                reject(new Error(`Failed to load script: ${src}`));
                };
                document.head.appendChild(script);
            });
        }"""

        self.page.wait_for_timeout(500)

        self.page.evaluate(script)

    def drag_bounds_to_coords(self, mouse, corners, steps=3):
        desired_corners = self.convert_scan_to_px(corners)
        actual_corners = self.get_current_map_points()

        pairs = pair_by_angle(desired_corners, actual_corners)

        for actual, goal in pairs:
            self.drag_point(mouse, actual, goal, steps=steps)

    def drag_point(self, mouse, actual, goal, steps=3):
        self.canvas.bounding_box()
        actual = self.correct_frame(actual)
        goal = self.correct_frame(goal)

        mouse.move(actual["x"], actual["y"], steps=steps)
        mouse.down()
        mouse.move(goal["x"], goal["y"], steps=steps)
        mouse.up()

    def correct_frame(self, point):
        bounding = self.canvas.bounding_box()

        return {"x": point["x"] + bounding["x"], "y": point["y"] + bounding["y"]}

    def map_change(self):
        class MapChange:
            def __init__(self, map: Map):
                self.map = map
                self.bounds_changed = None
                self.rendered_changed = None

            def __enter__(self):
                self.bounds = self.map.get_bounds()
                self.rendered = self.map.get_rendered_object_count()

            def __exit__(self, *_):
                self.map.wait_for_not_zooming()
                self.bounds_changed = self.bounds != self.map.get_bounds()
                self.rendered_changed = (
                    self.map.get_rendered_object_count() - self.rendered
                )

        return MapChange(self)

    @contextmanager
    def poll_for_map_change(self, attempts=10):
        points = self.get_rendered_object_count()

        yield

        for _ in range(attempts):
            new_points = self.get_rendered_object_count()
            if points != new_points:
                return True

            self.page.wait_for_timeout(200)

        raise TimeoutError
