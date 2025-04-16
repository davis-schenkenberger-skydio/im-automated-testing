import os
import re


def _convert_lat_lng(inp):
    inp = inp.replace(" ", "")
    coords = map(float, inp.split(","))

    return tuple(coords)


# Address for map search testing
ADDRESS_QUERY = os.environ["ADDRESS_QUERY"]
ADDRESS_LOCATION = _convert_lat_lng(os.environ["ADDRESS_LOCATION"])

# Mission name and regex
DEFAULT_MISSION_NAME_RE = re.compile(os.environ["DEFAULT_MISSION_NAME_RE"])
MISSION_NAME = os.environ["MISSION_NAME"]

# Site/Dock location
SITE_NAME = os.environ["SITE_NAME"]
SITE_LOCATION = _convert_lat_lng(os.environ["SITE_LOCATION"])
DOCK_NAME = os.environ["DOCK_NAME"]

SCAN_CORNERS = [
    [-122.33145073709481, 37.53443411899255],
    [-122.33209049443792, 37.53376102376943],
    [-122.33129044828988, 37.533280247471254],
    [-122.33064006334622, 37.533942581363306],
]

TESTRAIL_KEY = os.environ["TESTRAIL_KEY"]
TESTRAIL_URL = os.environ["TESTRAIL_URL"]
TESTRAIL_EMAIL = os.environ["TESTRAIL_EMAIL"]
TESTRAIL_RUN_ID = int(os.environ["TESTRAIL_RUN_ID"])
