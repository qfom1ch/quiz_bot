from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config_data.config import DATABASE

engine = create_engine(DATABASE, echo=False)

Session = sessionmaker()
Session.configure(bind=engine)

session = Session()
