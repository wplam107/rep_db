import configparser
import firebase_admin
from firebase_admin import credentials, firestore

class Auth():
    def __init__(self, file):
        self.config = configparser.ConfigParser()
        self.config.read(file)
        self.fb_app = None
        
    def auth_propub(self):
        PROPUBLICA_API_KEY = self.config.get('propublica', 'PROPUBLICA_API_KEY')
        self.pp_root = 'https://api.propublica.org/congress/v1/'
        self.pp_header = {'X-API-Key': f'{PROPUBLICA_API_KEY}'}
    
    def get_propub(self):
        '''
        Return API_ROOT and header for ProPublica (strings)
        '''

        return self.pp_root, self.pp_header

    def auth_db(self):
        if self.fb_app == None:
            GCP_AUTH_PATH = self.config.get('firebase', 'GCP_AUTH_PATH')
            cred = credentials.Certificate(GCP_AUTH_PATH)
            self.fb_app = firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        else:
            print('Connection already established')

    def get_db(self):
        '''
        Return db (object)
        '''

        return self.db