from sqlalchemy import create_engine
from utils.constants import *

def get_engine():
    db_connection_url = "postgresql://{}:{}@{}:{}/{}".format(
        USERNAME,
        PASSWORD,
        HOST,
        PORT,
        DATABASE_NAME
    )
    return create_engine(db_connection_url)