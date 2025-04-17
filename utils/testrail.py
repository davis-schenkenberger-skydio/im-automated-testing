import requests
from requests.auth import HTTPBasicAuth


class TestRail:
    def __init__(self, host: str, email: str, api_key: str):
        self.auth = HTTPBasicAuth(email, api_key)
        self.host = host
        self.headers = {"Content-Type": "application/json"}

    def request(self, method: str, endpoint: str, **args):
        url = f"{self.host}/index.php?/api/v2/{endpoint}"
        response = requests.request(
            method, url, auth=self.auth, headers=self.headers, **args
        )
        print(response.text)
        response.raise_for_status()

        return response.json()

    def get(self, endpoint: str, **args):
        return self.request("GET", endpoint, **args)

    def post(self, endpoint: str, **args):
        return self.request("POST", endpoint, **args)

    def get_test_results_for_case(self, run_id: int, case_id: int):
        r = self.get(f"get_results_for_case/{run_id}/{case_id}")

        return r

    def get_case(self, case_id: int):
        return self.get(f"get_case/{case_id}")

    def add_results(self, test_id, test_results: dict):
        self.post(f"add_result/{test_id}", json=test_results)

    def add_results_for_cases(self, run_id: int, test_results: dict):
        self.post(f"add_results_for_cases/{run_id}", json=test_results)
