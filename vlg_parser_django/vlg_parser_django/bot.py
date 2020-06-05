# -*- coding: utf-8 -*-
"""
Чат-бот для предмета Основы трансляции
"""

import requests
import re
import os
import json
from time import sleep
from dotenv import load_dotenv
from collections import OrderedDict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, 'vlg_parser_django', '.env'))


TELEGRAM_PROXY = os.getenv("TELEGRAM_PROXY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PROXIES = {'https': TELEGRAM_PROXY}

URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'

REGEXP = r'\d{1,3}([, ]\d{3})*(\.\d+)?'


def get_updates_json():
    """
    Получаем JSON-строку ответа на запрос getUpdates
    """
    # Ждём ответа на протяжении заданного  в параметре timeout числа секунд
    params = {'timeout': 100, 'offset': None}
    # Выполняем Get-запрос, возвращается объект ответа
    response = requests.get(URL + 'getUpdates', data=params, proxies=PROXIES)
    # Из объекта ответа берём JSON
    return response.json()


def last_update(response_json):
    """
    Получает последнее событие от бота
    :param response_json:
    :return:
    """
    # Обращаемся к словарю по ключу result
    results = response_json['result']
    # Последнее событие - последнее по порядку минус 1, т.к. нумерация с нуля
    last_update_index = len(results) - 1
    # Возвращаем последнее событие
    return results[last_update_index]


def get_chat_id(result_json):
    """
    Получает идентификатор чата, от которого пришло сообщение
    """
    # Смотрим по JSON, message -> chat -> id
    return result_json['message']['chat']['id']


def get_update_id(result_json):
    """
    Получает идентификатор последнего события в чате
    """
    # Возвращаем идентифиатор последнего события
    return result_json['update_id']


#
def send_message(chat_id, text):
    """
    Отправляет пришедшее событие назад
    """
    # Формируем параметры запроса: куда и что отправляем
    params = {'chat_id': chat_id, 'text': text}
    # Отправляем Post-запрос, возвращаем объект ответа
    return requests.post(URL + 'sendMessage', data=params, proxies=PROXIES)


def check_number(message, updates_json):
    """
    Проверяет является ли число корректным
    """
    # Проверяем regex
    found = re.fullmatch(REGEXP, message)
    # Если подходит отправляем сообщение
    if found:
        send_message(
            get_chat_id(updates_json),
            "Число является корректным с запятой или пробелом, в качестве разделителя разрядов"
        )

def show_all_entries(message, updates_json):
    with open('data.json', 'r') as json_file:
        database_data = json.load(json_file)
    data = {f'{data.get("surname")} {data.get("name")}': data for user_id, data in database_data.items()}

    data_keys = sorted(list(data.keys()))

    list_of_tuples = [(key, data[key]) for key in data_keys]
    ordered_data_dict = OrderedDict(list_of_tuples)
    message = ''
    for _, entry_data in ordered_data_dict.items():
        message += f"""ID: {entry_data.get('id')}
Тел. {entry_data.get('number')}
Фамилия: {entry_data.get('surname')}
Имя: {entry_data.get('name')}
"""
        if entry_data.get('vk'):
            message += f"Вконтакте: {entry_data.get('vk')}\n"
        if entry_data.get('vk'):
            message += f"Телеграм: {entry_data.get('telegram')}\n"
        message += '\n'

        send_message(get_chat_id(updates_json), message)

def add_entry(message, updates_json):
    with open('data.json', 'r') as json_file:
        database_data = json.load(json_file)
    data_list = message.split(' ')
    data_dict = {
        'number': data_list[1],
        'surname': data_list[2],
        'name': data_list[3]
    }
    for data_entry in data_list:
        if 'vk:' in data_entry:
            data_dict.update({'vk': data_entry})
        if 't:' in data_entry:
            data_dict.update({'telegram': data_entry})
    user_id = 0
    while True:
        if user_id not in list(database_data.keys()):
            data_dict.update({'id': user_id})
            database_data.update({user_id: data_dict})
            break
        user_id += 1
    with open('data.json', 'w') as json_file:
        json.dump(database_data, json_file)
    send_message(
        get_chat_id(updates_json),
        "Запись добавлена"
    )

def del_entry(message, updates_json):
    with open('data.json', 'r') as json_file:
        database_data = json.load(json_file)
    message_list = message.split(' ')
    id_to_delete = message_list[-1]
    database_data.pop(int(id_to_delete))
    with open('data.json', 'w') as json_file:
        json.dump(data, json_file)
    send_message(
        get_chat_id(updates_json),
        f"Запись ID: {id_to_delete} удалена"
    )

def del_all_entries(message, updates_json):
    with open('data.json', 'w') as json_file:
        data = {}
        json.dump(data, json_file)
        send_message(
            get_chat_id(updates_json),
            f"Все записи удалены"
        )

def process_message(message, updates_json):
    functions_dict = {
        '/show all': show_all_entries,
        '/del all': del_all_entries,
        '/add': add_entry,
        '/del': del_entry
    }
    for prefix, function in functions_dict.items():
        if message.startswith(prefix):
            function(message, updates_json)
            break

def check_maket(message, updates_json):
    if 'где макет' in message.lower():
        send_message(get_chat_id(updates_json), "Будет в понедельник")

def main():
    """
    Точка входа в программу
    """
    # Получаем идентификатор самого последнего события
    last_update_id = get_update_id(last_update(get_updates_json()))
    # Бот работает в вечном цикле, нужно будет принудительно останавливать
    while True:
        # Получаем последнее событие на текущий момент
        updates_json = last_update(get_updates_json())
        # Получаем его идентификатор
        current_update_id = get_update_id(updates_json)

        # Если было новое событие, отправляем сообщение и запоминаем его идентификатор
        if current_update_id != last_update_id:
            message = updates_json['message'].get('text')
            check_number(message, updates_json)
            process_message(message, updates_json)
            check_maket(message, updates_json)
            last_update_id = current_update_id
        # Ждём одну секунду
        sleep(1)


if __name__ == '__main__':
    main()

