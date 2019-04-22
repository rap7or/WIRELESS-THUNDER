import requests
import pytest

def login(data):
    try:
        r = requests.post("https://localhost", data=data, verify=False)
    except Exception as e:
        print(e)
        return None
    return r.status_code

def main():
    data = {"username": "Jack", "password":"jackand"}
    y = login(data)
    if y != 200:
        print("unsuccessful login")
    else:
        print("Successful Login")

if __name__ == "__main__":
    main()
