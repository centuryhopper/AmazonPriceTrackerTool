import requests
from fake_useragent import UserAgent
import random

ua = UserAgent(use_cache_server=False, fallback='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36')
HEADERS = {'User-Agent': ua.random}

def get_proxy_list():
    # proxy_list = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt', headers=HEADERS).text.split('\n')
    proxy_list = []
    with open('Proxies/proxies.txt', 'r') as f:
        proxy_list = f.read().split("\n")
    return proxy_list

def get_working_proxies(proxy_list=[]):
    working = []
    for proxy in proxy_list:
        if proxy != '':
            try:
                r = requests.get('https://www.amazon.com/dp/B083W6328Q', headers=HEADERS, proxies={'https': proxy}, timeout=random.randint(1,3))
                if r.status_code == 200:
                    print(f'{proxy} is working!')
                    working.append(proxy)
            except:
                print(f"{proxy} is not working.")
                pass
    return working

print(HEADERS)
lst = get_proxy_list()
print(len(lst))
print(get_working_proxies(lst))



