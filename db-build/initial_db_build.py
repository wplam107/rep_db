# Config reader
import configparser

# Database connection and authentication
import firebase_admin
from firebase_admin import credentials, firestore

# Data acquisition / ETL functions
from etl_functions import *

def main():
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read('./auth/config.ini')

    # Get ProPublica Auth
    PROPUBLICA_API_KEY = config.get('propublica', 'PROPUBLICA_API_KEY')
    API_ROOT = 'https://api.propublica.org/congress/v1/'
    header = {'X-API-Key': f'{PROPUBLICA_API_KEY}'}

    # Get Google Firebase Auth
    GCP_AUTH_PATH = config.get('firebase', 'GCP_AUTH_PATH')
    cred = credentials.Certificate(GCP_AUTH_PATH)
    app = firebase_admin.initialize_app(cred)

    # Instantiate connection to database
    db = firestore.client()
    print('Database Authenticated...')

    # House member ids of the 116-117th Congress (2018-2022)
    ids_116 = get_house_ids(116, API_ROOT, header)
    ids_117 = get_house_ids(117, API_ROOT, header)
    print('IDs Collected...')

    # Create list of unique IDs to remove redundant API calls
    all_ids = list(set(ids_116 + ids_117))

    # Generator for representative data
    reps = ( get_member_data(mem, API_ROOT, header) for mem in all_ids )

    # Generator for cleaned representative data
    cleaned_reps = ( member_cleaner(rep) for rep in reps )

    # Batch insert data
    batch_insert(
        docs=cleaned_reps,
        db=db,
        col_name='reps',
        _id='_id',
        with_ids=True
    )

if __name__ == '__main__':
    main()