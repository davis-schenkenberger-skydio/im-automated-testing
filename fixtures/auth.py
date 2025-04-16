from pathlib import Path

import pytest

from pages.login_page import Login

AUTH_FILE = Path("playwright/.auth/state.json")


@pytest.fixture
def auth_page(new_context, cloud_email: str):
    context_args = {"permissions": []}

    if AUTH_FILE.exists():
        context = new_context(
            storage_state="playwright/.auth/state.json", **context_args
        )
    else:
        context = new_context(**context_args)

    page = context.new_page()
    page.goto("/")

    login = Login(page)

    try:
        page.wait_for_url("**/fleet", timeout=10_000)
    except TimeoutError:
        print("WAITING FOR USER TO LOGIN")
        login.goto()
        login.fill(cloud_email, None)
        page.wait_for_url("**/fleet", timeout=120_000)
        context.storage_state(path=AUTH_FILE)

    # Set default timeout to be a bit longer
    context.set_default_timeout(60_000)

    yield page

    context.close()
