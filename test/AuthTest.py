import requests
import pytest
import sys

def reg_request(data):
    try:
        r = requests.post("https://localhost/register", data=data, verify=False)
    except Exception as e:
        print(e)
        return None
    return r

def login(data):
    try:
        r = requests.post("https://localhost/login", data=data, verify=False)
    except Exception as e:
        print(e)
        return None
    return r.status_code

def main():
    data = {"username": "Jack", "password":"jackandjill"}
    x = reg_request(data)
    if x == None:
        print("couldn't register")
        sys.exit()
    y = login(data)
    if y!= 200:
        print("unsuccessful login")
    else:
        print("Successful Login")

if __name__ == "__main__":
    main()
