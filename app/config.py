from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('.ini')

class Config:
    """Flask configuration variables."""

    # General Config
    FLASK_APP = cfg.get('webapp', 'FLASK_APP')
    FLASK_ENV = cfg.get('webapp', 'FLASK_ENV')
    SECRET_KEY = cfg.get('webapp', 'SECRET_KEY')