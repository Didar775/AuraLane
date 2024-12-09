import requests
from django.http import JsonResponse
from django.core.cache import cache
from trendhive.settings import get_env_variable


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
    response = requests.get(f'{get_env_variable("API_BASE_URL")}items/', headers=headers)
    if response.status_code == 200:
        categories = response.json()
        for category in categories:
            Category.objects.update_or_create(
                id=category['id'],
                defaults={
                    'name': category['name'],
                    'archived': category['archived'],
                    'href': category['href']
                }
            )
    return f'{len(categories)} categories updated'


@shared_task
def fetch_items_from_crm():
    headers = {'Authorization': f'Bearer {get_access_token()}'}
    response = requests.get(f'{get_env_variable("API_BASE_URL")}categories/', headers=headers)
    print(headers, "\n\n\n\n\n")
    if response.status_code == 200:
        items = response.json()
        for item in items:
            Item.objects.update_or_create(
                id=item['id'],
                defaults={
                    'name': item['name'],
                    'description': item['description'],
                    'code': item['code'],
                    'buy_price': item['buy_price'],
                    'sale_price': item['sale_price'],
                    'category_id': item['category'],
                    'weight': item['weight'],
                    'in_stock': item['in_stock'],
                    'count': item['count'],
                    'sale_id': item.get('sale_id'),
                    'tags_id': item.get('tags_id'),
                    'shop_id': item.get('shop'),
                }
            )
    return f'{len(items)} items updated'
