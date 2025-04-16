import re


def matches(input: str, pattern: str | re.Pattern) -> bool:
    if isinstance(pattern, str):
        return re.search(pattern, input) is not None
    else:
        return pattern.match(input) is not None
