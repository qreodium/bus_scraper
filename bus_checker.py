import requests
from bs4 import BeautifulSoup
import re
import sys
import pyexcel as pe
from pyexcel_ods import save_data
from collections import OrderedDict
from datetime import datetime
import os.path


headers={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "ru,en;q=0.9,la;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://na-avtobus.ru/raspisanie/kya/krasnoyarsk-zhd/kya/zheleznogorsk/2021-09-16/2021-09-16/",
    "sec-ch-ua": '\" Not;A Brand\";v=\"99", \"Yandex\";v=\"91\", \"Chromium\";v=\"91\"',
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.135 YaBrowser/21.6.2.817 (beta) Yowser/2.5 Safari/537.36"
    }
response = requests.get(f"https://na-avtobus.ru/raspisanie/kya/krasnoyarsk-zhd/kya/zheleznogorsk/{datetime.now().strftime('%Y-%m-%')}", headers)
if(response.status_code == 200):
    sys.exit(f"Error! The server did not send the necessary data. Response status code:{response.status_code}")

soup = BeautifulSoup(response.text, 'lxml')
tickets_list = soup.find_all("div" , attrs = { "class" : "tickets"})

for ticket in tickets_list:
    seats_html = ticket.find("div",  attrs = { "class" : "view-select"})
    seats = seats_html.find("span", attrs = { "class" : None})
    if(seats):
        print(re.search(r'\d+',seats.text).group(0))
    elif(seats_html.find("p", attrs = { "class" : "no-places"})):
        print("0 нет мест")
    elif(seats_html.find("a", attrs = { "class" : "support", "tabindex": "1"})):
        print("Продажа закрыта")

print(datetime.now().strftime('%d-%m-%y'))

if(os.path.isfile('your_file.ods')):
    book = pe.get_sheet(file_name="your_file.ods")
    book.column += [12, 11, 10]
    book.save_as("your_file.ods")
else:
    data = OrderedDict()
    data.update({datetime.now().strftime('%d-%m-%y'): [['07:40'], ["08:20"], ["09:10"], ["10:10"], ["11:30"], ["12:20"], ["13:10"], ["14:50"], ["16:30"], ["17:10"], ["17:50"], ["18:30"], ["19:10"], ["20:30"], ["23:00"]]})
    save_data("your_file.ods", data)
