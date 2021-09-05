from sqlalchemy import create_engine
from yaml.loader import SafeLoader
import yaml
import os

def get_engine():
    # Load db_config.yaml
    with open(os.path.join('conf', 'db_config.yml')) as f:
        data = yaml.load(f, Loader=SafeLoader)
    db_connection_url = "postgresql://{}:{}@{}:{}/{}".format(
        data['postgres']['username'],
        data['postgres']['password'],
        data['postgres']['host'],
        data['postgres']['port'],
        data['postgres']['db']
    )
    return create_engine(db_connection_url)