import requests
import pytest



def make_request(url):
    try:
        r = requests.get(url=url, timeout=10)
    except Exception as e:
        print(e)
        return None
    return r


def test_hello_world(url):
    request = make_request(url)
    assert request != None
    assert request.status_code == 200
    assert "Hello World" in request.text


def main():
    url = "http://localhost"
    test_hello_world(url)


if __name__ == "__main__":
    main()
