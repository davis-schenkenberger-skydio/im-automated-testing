import pytest

import data.config as cfg
from utils.testrail import TestRail


def pytest_addoption(parser):
    parser.addoption(
        "--report-to-testrail",
        action="store_true",
        default=False,
        help="Enable reporting test results to TestRail",
    )


def pytest_configure(config):
    if config.getoption("--report-to-testrail"):
        config.testrails = TestRail(
            cfg.TESTRAIL_URL, cfg.TESTRAIL_EMAIL, cfg.TESTRAIL_KEY
        )
    else:
        config.testrails = None


results = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":  # Only consider the actual test call
        mark = item.get_closest_marker("testrail")
        if mark:
            case_ids = mark.kwargs.get("id", [])
            if not isinstance(case_ids, list):
                case_ids = [case_ids]

            status = 1 if report.passed else 5
            comment = report.longreprtext if report.failed else "Test passed"
            duration = report.duration  # in seconds

            for case_id in case_ids:
                results[case_id] = (status, comment, duration)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    tr: TestRail = session.config.testrails

    if tr is None:
        return

    print()
    for case_id, (status, comment, duration) in results.items():
        test_results = tr.get_test_results_for_case(cfg.TESTRAIL_RUN_ID, case_id)
        test_id = test_results["results"][0]["test_id"]

        print(f"Reporting {case_id} to TestRail with status {status}")
        tr.add_results(
            test_id,
            test_results={
                "status_id": status,
                "comment": comment,
                "elapsed": f"{duration:.2f}s",
            },
        )
