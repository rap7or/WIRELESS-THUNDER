import requests
import pytest
from bs4 import BeautifulSoup


def make_request(url):
    try:
        r = requests.get(url=url, timeout=10, verify=False)
    except Exception as e:
        print(e)
        return None
    return r


def test_hello_world(url="http://localhost"):
    request = make_request(url)
    assert request is not None
    assert request.status_code == 200
    html = BeautifulSoup(request.text)
    assert "Login" in html.title.text


def main():
    test_hello_world()


if __name__ == "__main__":
    main()
