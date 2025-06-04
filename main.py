import time
from csv_writer import write_first_row_csv
from exceptions import StatusCode403, StatusCodeNot200
from parser import GoldAppleParser


def main():
    """
    Основная функция для запуска парсинга данных с сайта GoldApple.
    """
    products_url = "https://goldapple.ru/front/api/catalog/products"
    product_card_url = "https://goldapple.ru/front/api/catalog/product-card"
    city_id = "0c5b2444-70a0-4932-980c-b4dc0d3f02b5"  # - Москва
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/119.0.0.0 Safari/537.36'
    }

    write_first_row_csv()

    parser = GoldAppleParser(products_url, product_card_url, city_id, headers)

    current_page = 1
    total_parsed = 0

    while True:
        try:
            parsed_on_page = parser.parse_page(current_page)
            if parsed_on_page == 0:
                break
            total_parsed += parsed_on_page
        except StatusCode403 as er:
            print(f'Вы забанены!: {er}')
            print(f'{er.answer_status_code}')
            print(f'{er.answer_text}')
            exit()
        except StatusCodeNot200 as er:
            print(f'Вы код ответа не 200!: {er}')
            print(f'{er.answer_status_code}')
            print(f'{er.answer_text}')
            input(f'Нажмите Enter, чтоб возобновить работу программы:')
        except Exception as er:
            print(f'Неизвестная ошибка!: {er}')
            print(f'{er.args}')
            input(f'Нажмите Enter, чтоб возобновить работу программы:')

        current_page += 1
        time.sleep(10)

    print(f'Парсинг завершён!')


if __name__ == '__main__':
    main()
