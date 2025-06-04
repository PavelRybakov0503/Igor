import csv
import os
from datetime import datetime

# Создание директории если ее нет
results_dir = 'result'
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

now = datetime.now()
formatted_date = now.strftime("%Y.%m.%d %H_%M_%S")
path_to_file = f'{results_dir}/{formatted_date}.csv'

def write_first_row_csv():
    try:
        with open(path_to_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    'Ссылка',
                    'Наименование',
                    'Цена',
                    'Рейтинг пользователей',
                    'Описание продукта',
                    'Инструкция по применению',
                    'Cтрана-производитель'
                )
            )
    except Exception as e:
        print(f'Ошибка при записи первой строки в CSV: {e}')

def write_data_csv(row):
    try:
        with open(path_to_file, 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(row)
    except Exception as e:
        print(f'Ошибка при записи данных в CSV: {e}')
