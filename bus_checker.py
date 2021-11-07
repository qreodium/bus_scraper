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
import configparser

def main():
    data_processing(request_html(f"https://na-avtobus.ru/raspisanie/kya/krasnoyarsk-zhd/kya/zheleznogorsk/{datetime.now(time_zone_KRA).strftime('%Y-%m-%d')}"),config.get("Settings", "Kra-Zhe_filename"))
    data_processing(request_html(f"https://na-avtobus.ru/raspisanie/kya/zheleznogorsk/kya/krasnoyarsk-zhd/{datetime.now(time_zone_KRA).strftime('%Y-%m-%d')}"),config.get("Settings", "Zhe-Kra_filename"))

def request_html(url):
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
    response = requests.get(url, headers)

    # Проверяем статус ответа
    if(response.status_code != 200):
        logger.error(f"Error! The server did not send the necessary data. Response status code:{response.status_code}")
    return response

def get_schedule(tickets_list, spreadsheet_filename):
    depature_date = re.search(r'\d+\s\w+', tickets_list[0].find("p", attrs = { "class" : "trip_head-data"}).get_text()).group(0)
    logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Loading or create schedule for tickets: {len(tickets_list)}")
    if os.path.isfile(spreadsheet_filename):
        book = pyexcel.get_book(file_name=spreadsheet_filename)
        if depature_date in book.sheet_names():
            writen_time = [value for value in book[depature_date].column_at(0) if value][:-1]
            schedule_times = {}.fromkeys(writen_time, None)
            logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Load schedule: {schedule_times}")
            return schedule_times
    schedule_times = {}
    for ticket in tickets_list:
        schedule_times.update({ticket["data-time"]: None})
    return schedule_times

def get_depature_date(tickets_list):
    raw_date = tickets_list[0].find("p", attrs = { "class" : "trip_head-data"}).get_text()
    return re.search(r'\d+\s\w+', raw_date).group(0)

def save_data(depature_date, schedule_times, spreadsheet_filename):
    book = None
    if os.path.isfile(spreadsheet_filename):
        book = pyexcel.get_book(file_name=spreadsheet_filename)
    else:
        logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Creating file bus_analytics.ods")
        book = pyexcel.Book({depature_date: [[time] for time in schedule_times]})
        logger.debug(book)

    if not (depature_date in book.sheet_names()):
        logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Creating new sheet in file")
        sheet = pyexcel.Sheet([[time] for time in schedule_times])
        sheet.name = depature_date
        logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} New sheet: {sheet}")
        book += sheet
        logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Finaly book: f{book}")
    book[depature_date].column += list(schedule_times.values())   
    book.save_as(spreadsheet_filename)

def fill_schedule(schedule_times, tickets_list):
    print(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Check!")
    if tickets_list:
        for ticket in tickets_list:
            depature_time = ticket["data-time"]
            #Сделать глобальным
            if(ticket["data-status"] == "ok"):
                seat = ticket["data-seats"]
                if schedule_times:
                    if depature_time in schedule_times:
                        schedule_times[depature_time] = seat;
        logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} Dep.date: {depature_time}  Check!")
        schedule_times.update({"check_time": datetime.now(time_zone_KRA).strftime('%H:%M:%S')})
        return schedule_times

def data_processing(response, spreadsheet_filename):
    # Подготавливаем файл для записи
    soup = BeautifulSoup(response.text, 'lxml')
    tickets_list = soup.find_all("div" , attrs = { "class" : "tickets"})
    if tickets_list: 
        depature_date = get_depature_date(tickets_list)
        schedule_times = get_schedule(tickets_list, spreadsheet_filename)
        logger.debug(f"This schedule: {schedule_times}")
        schedule_times = fill_schedule(schedule_times, tickets_list)
        print(f"Times: {schedule_times}")
    else:
        print(f"No tickets")
        logger.debug(f"{datetime.now(time_zone_KRA).strftime('%D %H:%M:%S')} None tickets_list!")

    # Получаем данные каждой доступной поездки, места, время. Записываем с ключем времени в словарь schedule_times количество свободных мест


    # Добавляем в него полученную информацию
    save_data(depature_date, schedule_times, spreadsheet_filename)

if __name__ == "__main__":
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read("config.ini")
    if not os.path.exists(config.get("Settings", "home_dir")):
        os.makedirs(config.get("Settings", "home_dir"))

    logger = logging.getLogger("bus")
    logger.setLevel(logging.DEBUG)

    # create the logging file handler
    fh = logging.FileHandler(config.get("Settings", "log_file"), mode='w')

    formatter = logging.Formatter('%(message)s - %(levelname)s')
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)

    time_zone_KRA = pytz.timezone('Asia/Krasnoyarsk')
    main()
    while True:
        if datetime.now(time_zone_KRA).hour == 23:
            logger.info("23 hours, waiting...")
            time.sleep(7*60*60)
            logger.info("Wake up an start working.")

        while not(datetime.now(time_zone_KRA).minute % 10 == 9):
            time.sleep(20)
        main()
        time.sleep(9*60)
