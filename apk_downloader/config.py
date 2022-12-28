import os

from dotenv import load_dotenv

load_dotenv("..\.env")

pghost = os.getenv('POSTGRES_HOST','localhost')
pgdb = os.getenv('POSTGRES_DB','db')
pguser = os.getenv('POSTGRES_USER','user')
pgpass = os.getenv('POSTGRES_PASSWORD','password')
pschema = os.getenv('POSTGRES_SCHEMA','public')
pgport = os.getenv('POSTGRES_PORT',5432)

apk_save_folder = os.getenv('APK_SAVE_FOLDER', r'c:\download')