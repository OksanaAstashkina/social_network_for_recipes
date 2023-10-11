"""Создание пользовательской команды импорта данных в БД из CSV-файла."""

import csv
import os
from pathlib import Path

from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

CSV_MODELS_FIELDS = {
    Ingredient: ('ingredients.csv', 'utf-8', None, None),
}
path_to_csv_directory = os.path.join(BASE_DIR, 'data/')


class Command(BaseCommand):
    """Класс импорта данных в БД из CSV-файла."""

    def handle(self, *args, **options):
        """Функция фактической логики импорта данных в БД из CSV-файла."""

        def csv_to_db(model, csv_file, csv_file_path, codec):
            """Чтение файла csv и добавление данных из него в БД."""
            with open(csv_file_path, 'r', encoding=codec) as data_csv_file:
                reader = csv.DictReader(data_csv_file)
                _, _, db_field, scv_field = CSV_MODELS_FIELDS[model]
                for row in reader:
                    if scv_field:
                        row[db_field] = row.pop(scv_field)
                    model.objects.create(**row)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Данные из файла {csv_file} успешно импортированы'
                        f' в таблицу БД {model.__name__}.'
                    )
                )
        for model, (csv_file, codec, _, _) in CSV_MODELS_FIELDS.items():
            csv_file_path = Path(path_to_csv_directory) / csv_file
            csv_to_db(model, csv_file, csv_file_path, codec)
