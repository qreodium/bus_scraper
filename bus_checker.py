import requests
from bs4 import BeautifulSoup
import re
import sys
import pyexcel
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

if(response.status_code != 200):
    sys.exit(f"Error! The server did not send the necessary data. Response status code:{response.status_code}")


schedule_times = {
    "07:40": None,
    "08:20": None,
    "09:10": None,
    "10:10": None,
    "11:30": None,
    "12:20": None,
    "13:10": None,
    "14:50": None,
    "16:30": None,
    "17:10": None,
    "17:50": None,
    "18:30": None,
    "19:10": None,
    "20:30": None,
    "23:00": None
}
soup = BeautifulSoup(response.text, 'lxml')
tickets_list = soup.find_all("div" , attrs = { "class" : "tickets"})

for ticket in tickets_list:
    depature_time = ticket["data-time"]
    if(ticket["data-status"] == "ok"):
        seat = ticket["data-seats"]
        print(seat)
        schedule_times[depature_time] = seat;
schedule_times.update({"check_time": datetime.now().strftime('%H:%M:%S')})
   

print(datetime.now().strftime('%d-%m-%y'))
print(list(schedule_times.values()))

if(os.path.isfile('bus_analytics.ods')):
    book = pyexcel.get_book(file_name="bus_analytics.ods")
    sheet = book.sheet_by_name(datetime.now().strftime('%d-%m-%y'))
    book[datetime.now().strftime('%d-%m-%y')].column += list(schedule_times.values())
    book.save_as("bus_analytics.ods")
else:
    data = OrderedDict()
    data.update({datetime.now().strftime('%d-%m-%y'): [["07:40"], ["08:20"], ["09:10"], ["10:10"], ["11:30"], ["12:20"], ["13:10"], ["14:50"], ["16:30"], ["17:10"], ["17:50"], ["18:30"], ["19:10"], ["20:30"], ["23:00"]]})
    save_data("bus_analytics.ods", data)
