import re
import requests
import json

from csv_writer import write_data_csv


class GoldAppleParser:
    """
    Класс для парсинга данных с сайта GoldApple.
    """

    def __init__(self, products_url: str, product_card_url: str, city_id: str, headers: dict):
        """
        Инициализация парсера.

        Args:
            products_url (str): URL для получения списка товаров.
            product_card_url (str): URL для получения информации о карточке товара.
            city_id (str): Идентификатор города.
            headers (dict): Заголовки запроса.
        """
        self.products_url = products_url
        self.product_card_url = product_card_url
        self.city_id = city_id
        self.headers = headers

    def get_products(self, page=1) -> dict:
        """
        Получает список товаров с указанной страницы.

        Args:
            page (int): Номер страницы с товарами.

        Returns:
            dict: JSON-ответ, содержащий список товаров.
        """
        data = {
            "categoryId": 1000000007,  # категория Парфюмерия
            "cityId": self.city_id,
            "cityDistrict": None,
            "pageNumber": page,
            "filters": []
        }
        response = requests.post(url=self.products_url, headers=self.headers, data=json.dumps(data))
        return response.json()

    def get_product_card(self, product_id: str) -> requests.Response:
        """
        Получает информацию о карточке товара по его ID.

        Args:
            product_id (str): ID товара.

        Returns:
            Response: HTTP-ответ с информацией о карточке товара.
        """
        data = {
            "itemId": product_id,
            "cityId": self.city_id,
            "cityDistrict": None,
            "customerGroupId": "0"
        }
        response = requests.post(url=self.product_card_url, headers=self.headers, data=json.dumps(data))
        return response

    def parse_products(self, response: dict) -> list:
        """
        Парсит информацию о товарах из JSON-ответа.

        Args:
            response (dict): JSON-ответ, содержащий список товаров.

        Returns:
            list: Список кортежей с информацией о товарах.
        """
        products_info = []
        products_raw = response.get('data', {}).get('products', [])
        for product in products_raw:
            product_id = product.get('itemId', '')
            product_url = "https://goldapple.ru" + product.get('url', '/404')
            name = product.get('name', '')
            price = product.get('price', {}).get('actual', {}).get('amount', '')
            rating = product.get("reviews", {}).get("rating", "")
            products_info.append((product_id, product_url, name, price, rating))
        return products_info

    def parse_country(self, text: str) -> str:
        """
        Извлекает информацию о стране из текста.

        Args:
            text (str): Текст, содержащий информацию о стране.

        Returns:
            str: Название страны.
        """
        try:
            return re.search(r'<br>(.*?)<br>', text).group(1)
        except AttributeError:
            return ''

    def parse_product_card(self, response: requests.Response) -> tuple:
        """
        Парсит информацию о карточке товара из JSON-ответа.

        Args:
            response (Response): HTTP-ответ с информацией о карточке товара.

        Returns:
            tuple: Кортеж с информацией о товаре, например (название, цена, описание, страна и т.д.).
        """
        if response.status_code != 200:
            return None

        product_data = response.json()
        name = product_data.get('name', '')
        price = product_data.get('price', {}).get('actual', {}).get('amount', '')
        description = product_data.get('description', '')

        country = self.parse_country(description)

        return name, price, description, country

    def parse_page(self, page_number: int) -> int:
        """
        Парсит страницу товаров и сохраняет результаты в CSV-файл.

        Args:
            page_number (int): Номер страницы с товарами.

        Returns:
            int: Количество спарсенных товаров на странице.
        """
        print(f'-' * 33)
        print(f'Страница: {page_number}')
        products_counter = 0
        products_res = self.get_products(page_number)
        products = self.parse_products(products_res)
        if len(products) == 0:
            return 0
        for product in products:
            product_id, product_info1 = product[0], product[1:]
            product_res = self.get_product_card(product_id)
            product_info2 = self.parse_product_card(product_res)
            products_counter += 1
            product_full_info = product_info1 + product_info2
            write_data_csv(product_full_info)
        return products_counter