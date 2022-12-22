import csv
import os

from django.core.management.base import BaseCommand, CommandError

from backend.settings import BASE_DIR
from foodgram.models import Ingredient


class Command(BaseCommand):
    """
    Добавляем ингредиенты из CSV файла
    """
    help = 'loading ingredients from data in json or csv'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            with open(os.path.join(BASE_DIR, options['filename']), 'r',
                      encoding='utf-8') as f:
                data = csv.reader(f)
                for row in data:
                    pk, name, measurement_unit = row
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в директорию data')
