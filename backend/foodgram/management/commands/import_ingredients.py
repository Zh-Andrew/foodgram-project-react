import os

import psycopg2
from django.core.management.base import BaseCommand
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())


class Command(BaseCommand):
    help = 'Импорт ингредиентов, которые чаще всего употребляются'

    def handle(self, *args, **kwargs):
        conn = psycopg2.connect(
            "host={0} dbname={1} user={2} password={3}".format(
                os.getenv('DB_HOST'),
                os.getenv('DB_NAME'),
                os.getenv('POSTGRES_USER'),
                os.getenv('POSTGRES_PASSWORD')
            )
        )
        cur = conn.cursor()
        csv_path = './ingredients.csv'
        cur.execute(
            "COPY foodgram_ingredient (id, name, measurement_unit) "
            "FROM '{0}' DELIMITER ',' CSV ENCODING 'UTF8' QUOTE '\"'".format(
                csv_path
            )
        )
        conn.commit()
