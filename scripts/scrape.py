import sys
from pathlib import Path

from bs4 import BeautifulSoup

TARGET = Path(sys.argv[1])


if __name__ == "__main__":
    with open(TARGET) as r:
        soup = BeautifulSoup(r.read())

        for row in soup.find_all("tr", class_="caseRow"):
            id_elem = row.find("td", class_="id")
            text_elem = row.find("td", class_=None)

            id = id_elem.text.strip().lstrip("C")
            text = (
                text_elem.text.strip()
                .replace("\n", " ")
                .replace("  ", " ")
                .replace('"', '\\"')
            )

            print(f'TEST_{id} = "{id} - {text}"')
