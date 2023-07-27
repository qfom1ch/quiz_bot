import os
import pathlib

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

DATABASE_ENGINE = 'sqlite:///'
DATABASE_DIR = pathlib.Path.cwd()
DATABASE_NAME = 'databasequiz.db'
DATABASE = ''.join(
    [DATABASE_ENGINE, os.path.join(DATABASE_DIR, DATABASE_NAME)])
