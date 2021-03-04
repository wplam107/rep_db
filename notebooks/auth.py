import configparser
import pymongo

class Auth():
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get_sections(self):
        return self.config.sections()

    def get_section_keys(self, section):
        return self.config._sections[section].keys()

    def get_configs(self, section):
        values = [ val for val in self.config._sections[section].values() ]
        return values

    def config_mongodb(self):
        uri, mongodb = self.get_configs('mongodb')
        client = pymongo.MongoClient(uri)
        db = client.get_database(mongodb)

        return db

