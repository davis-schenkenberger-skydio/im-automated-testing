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


test_results = {}


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
                test_results[case_id] = (status, comment, duration)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    tr: TestRail = session.config.testrails

    if tr is None:
        return

    results = []
    for case_id, (status, comment, duration) in test_results.items():
        if not isinstance(case_id, int):
            continue

        results.append(
            {
                "case_id": case_id,
                "status_id": status,
                "comment": comment,
                "elapsed": f"{duration:.2f}s",
            }
        )

    if results:
        tr.add_results_for_cases(cfg.TESTRAIL_RUN_ID, {"results": results})
        print("Test results have been reported to TestRail.")
    else:
        print("No TestRail results to report.")
