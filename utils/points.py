import math


def calculate_distance(p1, p2):
    return math.sqrt((p2["x"] - p1["x"]) ** 2 + (p2["y"] - p1["y"]) ** 2)


def compute_centroid(points):
    x_sum = sum(p["x"] for p in points)
    y_sum = sum(p["y"] for p in points)

    return {"x": x_sum / len(points), "y": y_sum / len(points)}


def angle_from_centroid(point, centroid):
    return math.atan2(point["y"] - centroid["y"], point["x"] - centroid["x"])


def sort_by_angle(points, centroid=None):
    centroid = centroid or compute_centroid(points)
    return sorted(points, key=lambda p: angle_from_centroid(p, centroid))


def pair_by_angle(desired_corners, actual_corners):
    centroid = compute_centroid(desired_corners + actual_corners)

    sorted_desired_corners = sort_by_angle(desired_corners, centroid)
    sorted_actual_corners = sort_by_angle(actual_corners, centroid)

    return zip(sorted_actual_corners, sorted_desired_corners, strict=False)


def midpoint(a, b):
    return {"x": (a["x"] + b["x"]) / 2, "y": (a["y"] + b["y"]) / 2}


def find_perpendicular_point(p1, p2):
    distance = calculate_distance(p1, p2)
    mp = midpoint(p1, p2)

    x1, y1 = p1["x"], p1["y"]
    x2, y2 = p2["x"], p2["y"]

    mx, my = mp["x"], mp["y"]
    dx, dy = x2 - x1, y2 - y1

    perp_dx, perp_dy = dy, -dx
    perp_length = distance / 2
    perp_dx, perp_dy = (
        perp_dx * (perp_length / math.sqrt(perp_dx**2 + perp_dy**2)),
        perp_dy * (perp_length / math.sqrt(perp_dx**2 + perp_dy**2)),
    )

    return {"x": mx + perp_dx, "y": my + perp_dy}
