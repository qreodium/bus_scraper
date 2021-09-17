import requests
import schedule
import time
from bs4 import BeautifulSoup
import re
import sys
import pyexcel
from collections import OrderedDict
from datetime import datetime
import os.path
import os

def main():
    data_processing(request_html())

def request_html():
    # Отправляем запрос
    headers={
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "ru,en;q=0.9,la;q=0.8",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https:#na-avtobus.ru/raspisanie/kya/krasnoyarsk-zhd/kya/zheleznogorsk/2021-09-16/2021-09-16/",
        "sec-ch-ua": '\" Not;A Brand\";v=\"99", \"Yandex\";v=\"91\", \"Chromium\";v=\"91\"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.135 YaBrowser/21.6.2.817 (beta) Yowser/2.5 Safari/537.36"
        }
    response = requests.get(f"https://na-avtobus.ru/raspisanie/kya/krasnoyarsk-zhd/kya/zheleznogorsk/{datetime.now().strftime('%Y-%m-%d')}", headers)

    # Проверяем статус ответа
    if(response.status_code != 200):
        sys.exit(f"Error! The server did not send the necessary data. Response status code:{response.status_code}")
    return response

def data_processing(response):
    # Получаем данные каждой доступной поездки, места, время. Записываем с ключем времени в словарь schedule_times количество свободных мест
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

    depature_date = re.match(r'[\d-]*', tickets_list[0].find("input", attrs = { "class" : "tripVariant"})["value"]).group(0)
    print(f"{datetime.now().strftime('%H:%M:%S')} Check!")
    for ticket in tickets_list:
        depature_time = ticket["data-time"]
        #Сделать глобальным
        if(ticket["data-status"] == "ok"):
            seat = ticket["data-seats"]
            schedule_times[depature_time] = seat;
    schedule_times.update({"check_time": datetime.now().strftime('%H:%M:%S')})

    book = None
    # Если нет файла, создаем и добавляем в него полученную информацию
    if not os.path.isfile('bus_analytics.ods'):
        book = pyexcel.Book({depature_date: [[time] for time in schedule_times]})
    else:
        book = pyexcel.get_book(file_name="bus_analytics.ods")
    if not (depature_date in book.sheet_names()):
        sheet = pyexcel.Sheet([[time] for time in schedule_times])
        sheet.name = depature_date
        book += sheet
    book[depature_date].column += list(schedule_times.values())   
    book.save_as("bus_analytics.ods")

def start_script():
    print(f"{datetime.now().strftime('%H:%M:%S')} Start working")
    schedule.every(1).minutes.until("23:30").do(main)

while not((datetime.now().minute % 10) % 9 == 0):
    time.sleep(10)

print((datetime.now().minute % 10) % 9)
print(datetime.now().minute)
main()

schedule.every(10).minutes.until("23:30").do(main)
schedule.every().day.at("15:08").do(start_script)

while True:
    schedule.run_pending()
    time.sleep(1)
