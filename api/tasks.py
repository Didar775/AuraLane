import requests
import logging
from django.http import JsonResponse
from django.core.cache import cache
from trendhive.settings import get_env_variable

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def login_to_crm():
    url = get_env_variable("API_BASE_URL")+"token/"
    data = {
        "username": get_env_variable("API_USERNAME"),
        "password": get_env_variable("API_PASSWORD")
    }
    response = requests.post(url, json=data)
    if response.status_code in [200, 201]:
        tokens = response.json()
        access_token = tokens['access']
        refresh_token = tokens['refresh']

        cache.set('crm_access_token', access_token, timeout=15)  # 15 минут
        cache.set('crm_refresh_token', refresh_token, timeout=15)  # 7 дней

        return access_token
    else:
        raise Exception('Can not authorize in CRM.')


def get_access_token():
    """Получаем access токен из кэша или делаем новый запрос"""
    token = cache.get('crm_access_token')
    if token:
        return token

    try:
        # Получаем новый токен через refresh токен
        refresh_token = cache.get('crm_refresh_token')
        if refresh_token:
            url = get_env_variable("API_BASE_URL") + "token/refresh/"
            response = requests.post(url, json={"refresh": refresh_token})
            if response.status_code == 200:
                token = response.json().get('access')
                cache.set('crm_access_token', token, timeout=15)  # Обновляем токен в кэше на 15 минут
                return token
    except Exception as e:
        print(f"Ошибка обновления токена: {e}")

    # Если не удалось обновить токен — делаем новый логин
    return login_to_crm()


import requests
from celery import shared_task
from catalog.models import Category, Item


@shared_task
def fetch_categories_from_crm():
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    response = requests.get(f'{get_env_variable("API_BASE_URL")}categories/', headers=headers)
    if response.status_code == 200:
        categories = response.json()
        for category_object in categories:
            category_data = category_object.get('category', {})
            if not category_data:
                logging.error(f"Категория отсутствует в объекте: {category_object}")
                continue

            category_id = category_data.get('id')
            if category_id is None:
                logging.error(f"Ключ 'id' отсутствует в категории: {category_data}")
                continue

            Category.objects.update_or_create(
                id=category_id,
                defaults={
                    'name': category_data.get('name', 'Без имени'),
                    'archived': category_data.get('archived', False),
                    'href': category_data.get('href', '#')
                }
            )
    return f'{len(categories)} categories updated'


@shared_task
def fetch_items_from_crm():
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    response = requests.get(f'{get_env_variable("API_BASE_URL")}items/', headers=headers)
    if response.status_code == 200:
        items = response.json()
        logging.error(f"Fetched items: {items}")  # Логируем данные для отладки

        for data in items:

            item = data['item']  # Извлекаем вложенный объект item
            category = data.get('category')  # Опционально обрабатываем category
            photos = data.get('photos', [])  # Список фото, если нужно

            item_instance, created = Item.objects.update_or_create(
                id=item['id'],
                defaults={
                    'name': item.get('name', 'Unknown Name'),
                    'description': item.get('description', ''),
                    'code': item.get('code', ''),
                    'buy_price': item.get('buy_price', 0.0),
                    'sale_price': item.get('sale_price', 0.0),
                    'category_id': item.get('category'),
                    'weight': item.get('weight', 0.0),
                    'in_stock': item.get('in_stock', False),
                    'sale_id': item.get('sale_id'),
                }
            )
            tags_ids = item.get('tags_id', [])
            if tags_ids:
                item_instance.tags.set(tags_ids)
    else:
        logging.error(f"Failed to fetch items: {response.status_code}, {response.text}")

    return f'{len(items)} items updated'


def decrement(item_id, count=1):
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    data = {
        "count": count
    }
    response = requests.post(f'{get_env_variable("API_BASE_URL")}items/{item_id}/transaction/', headers=headers, json=data)
    if response.status_code == 200:
        return True
    else:
        return False
