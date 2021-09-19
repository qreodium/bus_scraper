import pytz 
import requests
import time
from bs4 import BeautifulSoup
import re
import sys
import pyexcel
from datetime import datetime
import os.path
import logging

logger = logging.getLogger("bus")
logger.setLevel(logging.INFO)
    
# create the logging file handler
fh = logging.FileHandler("bus.log", mode='w')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s - %(levelname)s')
fh.setFormatter(formatter)

# add handler to logger object
logger.addHandler(fh)

time_zone_KRA = pytz.timezone('Asia/Krasnoyarsk') 

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
    response = requests.get(f"https://na-avtobus.ru/raspisanie/kya/krasnoyarsk-zhd/kya/zheleznogorsk/{datetime.now(time_zone_KRA).strftime('%Y-%m-%d')}", headers)

    # Проверяем статус ответа
    if(response.status_code != 200):
        sys.exit(f"Error! The server did not send the necessary data. Response status code:{response.status_code}")
    return response

def data_processing(response):

    # Подготавливаем файл для записи
    soup = BeautifulSoup(response.text, 'lxml')
    tickets_list = soup.find_all("div" , attrs = { "class" : "tickets"})
    schedule_times = {}
    book = None
    print(response.text)
    depature_date = re.match(r'[\d-]*', tickets_list[0].find("input", attrs = { "class" : "tripVariant"})["value"]).group(0)
    if os.path.isfile('bus_analytics.ods'):
        book = pyexcel.get_book(file_name="bus_analytics.ods")
        print(book.sheet_names())
        print(f" Normal? {depature_date}")
        print(depature_date in book.sheet_names())
        if depature_date in book.sheet_names():
            schedule_times = book[depature_date].column_at(1)
            print(schedule_times)
    # Получаем данные каждой доступной поездки, места, время. Записываем с ключем времени в словарь schedule_times количество свободных мест
    print(f"{datetime.now(time_zone_KRA).strftime('%H:%M:%S')} Check!")
    for ticket in tickets_list:
        depature_time = ticket["data-time"]
        #Сделать глобальным
        if(ticket["data-status"] == "ok"):
            seat = ticket["data-seats"]
            schedule_times[depature_time] = seat;
    logger.info(f"Dep.date: {depature_time} Check!")
    schedule_times.update({"check_time": datetime.now(time_zone_KRA).strftime('%H:%M:%S')})

    # Добавляем в него полученную информацию
    if not os.path.isfile('bus_analytics.ods'):
        logger.info("Creating file bus_analytics.ods")
        book = pyexcel.Book({depature_date: [[time] for time in schedule_times]})
        logger.info(book)

    if not (depature_date in book.sheet_names()):
        logger.info("Creating new sheet in file")
        sheet = pyexcel.Sheet([[time] for time in schedule_times])
        loger.info(f"New sheet: {sheet}")
        sheet.name = depature_date
        book += sheet
        loger.info(f"Finaly book: f{book}")
    book[depature_date].column += list(schedule_times.values())   
    book.save_as("bus_analytics.ods")


main()
