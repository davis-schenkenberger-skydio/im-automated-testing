import logging
import os

import pytest

pytest_plugins = ["fixtures.auth", "fixtures.mission", "fixtures.testrail"]


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--env", action="store", default="production", choices=["production", "env"]
    )


@pytest.fixture(scope="session")
def env_name(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def base_url(env_name, cloud_org):
    if env_name == "env" and (cloud_url := os.environ.get("CLOUD_URL")):
        logging.info("Using `CLOUD_URL` from environment")
        return cloud_url
    print(cloud_org)
    if env_name == "production":
        return f"https://cloud.skydio.com/o/{cloud_org}/"
    else:
        exit("Please provide an environment")


@pytest.fixture(scope="session")
def cloud_email():
    return os.environ["CLOUD_EMAIL"]


@pytest.fixture(scope="session")
def cloud_org():
    return os.environ["CLOUD_ORG"]
