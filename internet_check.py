import requests # pip install requests


def is_Online(url = "https://www.google.com",timeout = 5):
    try:
        responce = requests.get(url,timeout = timeout)
        return responce.status_code >= 200 and responce.status_code < 300
    except requests.ConnectionError:
        return False
    

