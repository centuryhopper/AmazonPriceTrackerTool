# import requests
# import time
# from time import sleep
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
# from win10toast import ToastNotifier

# '''
# code by Leo
# inspired by this link: https://www.youtube.com/watch?v=6Li6Y1_DRJ8&list=PLRzwgpycm-FiPfuP-bKOJTJRkQH-F8brg&index=3
# '''

# toaster = ToastNotifier()
# search = 'logitech k780' # Amazon Standard Identification Number: B01LZTBKBG
# searchProductDict = {}
# search_list = search.split()
# amazon_link = 'https://amazon.com'
# joinedSearch = '+'.join(search_list)
# url = f'{amazon_link}/s?k={joinedSearch}&ref=nb_sb_noss'


# def tracker(randomHeader):
#     '''
#     get all products related to the searched product and find the cheapest ones
#     '''
#     url_open = requests.get(url, headers=randomHeader)
#     soup = BeautifulSoup(url_open.content, 'lxml')
#     sleep(1)
#     tag = soup('span', {'class': 'a-size-medium a-color-base a-text-normal'})
#     tag2 = soup('span', {'class': 'a-price-whole'})
#     print(f'{len(tag)}\n\n{len(tag2)}')
#     # print(type(tag), type(tag2))
#     # grab all items
#     for i, j in zip(tag, tag2):
#         print(f'type(i.text): {type(i.text)} || type(j.text): {type(j.text)}')
#         # using in instead of == because i.text is generally going to be a longer string
#         if search.lower() in (i.text).lower():
#             # print(f'type(i.text): {type(i.text)} || type(j.text): {type(j.text)}')
#             print(f'found a {search.lower()} with price: {j.text} USD')
#             price = float(''.join(j.text.split(',')))
#             searchProductDict[i.text] = price

#             # go through each item and check
#             for productName, productPrice in searchProductDict.items():
#                 if i.text == productName:
#                     if price < productPrice:
#                         toaster.show_toast(
#                             'Amazon Deal', f'{i.text} || Price: {j.text} USD')
#                         print('Amazon Deal',
#                               f'{i.text} || Price: {j.text} USD')
#                         # TODO send twilio text to me


# while True:
#     user = UserAgent()
#     randomHeader = {'User-Agent': str(user.random)}
#     print('Tracking...', time.asctime(time.localtime(time.time())))
#     tracker(randomHeader)

#     # check every 5 minutes
#     sleep(60*5)
