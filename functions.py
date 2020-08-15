import requests



def r_get(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"}
    cookies = {}
    for i in range(5):
        try:
            result = requests.get(url, headers=headers, cookies=cookies, timeout=40)
            return result
        except:
            print(F'Failed. Retry {i+1}/5')
    print('Failed')
