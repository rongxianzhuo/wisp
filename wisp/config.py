import json


try:
    with open('settings.json', 'r', encoding='utf-8') as file:
        settings: dict = json.loads(file.read())
except Exception as e:
    settings = {}


def user_id():
    return settings.get('user_id', 'user')


def user_token():
    return settings.get('user_token', 'none')
