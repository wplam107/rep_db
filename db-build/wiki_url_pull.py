# Config reader
import configparser

# Database connection and authentication
import firebase_admin
from firebase_admin import credentials, firestore

# Google Knowledge Graph and WikiMedia
from googleapiclient.discovery import build
from mediawiki import MediaWiki

# Utils
import re
from googleapiclient.errors import HttpError

# Data acquisition / ETL functions
from etl_functions import *


def main():
    # Read config.ini file
    config = configparser.ConfigParser()
    config.read('./auth/config.ini')

    # Get Google Firebase Auth
    GCP_AUTH_PATH = config.get('firebase', 'GCP_AUTH_PATH')
    cred = credentials.Certificate(GCP_AUTH_PATH)
    app = firebase_admin.initialize_app(cred)

    # Retrieve Google GCP API Key from 'config.ini'
    GCP_API_KEY = config.get('gcpkeys', 'GCP_API_KEY')

    # Instantiate connection to database
    db = firestore.client()

    # Collection reference
    ref = db.collection('reps')

    # Get all representatives
    query = ref.where('_id', '!=', '').stream()
    members = [ doc.to_dict() for doc in query ]
    print('Updating data...')

    # Use Google API client
    service = build('kgsearch', 'v1', developerKey=GCP_API_KEY)
    entities = service.entities()

    # Get and set data
    errors = {}
    total = 0
    for mem in members:
        data, error = get_wikipedia(mem, entities)
        if error != None:
            e_type = type(error)
            if e_type not in errors.keys():
                errors[e_type] = []
            errors[e_type].append(mem)
        else:
            total += 1
        mem['wiki_url'] = data
    print(f'{total} Wikipedia URLs Added...')

    # List of errors to be corrected
    http_errors = errors[HttpError]
    key_errors = errors[KeyError]
    index_errors = errors[IndexError]
    _id_errors = index_errors + http_errors

    new_errors = {}
    for mem in _id_errors:
        # Get correct Google Entity ID
        _id, error = get_google_id(mem, entities)
        if error != None:
            e_type = type(error)
            if e_type not in new_errors.keys():
                new_errors[e_type] = []
            new_errors[e_type].append(mem)
        mem['google_id'] = _id

        # Get Wikipedia page with new Google Entity ID
        wiki_url, error = get_wikipedia(mem, entities)
        if error != None:
            e_type = type(error)
            if e_type not in new_errors.keys():
                new_errors[e_type] = []
            new_errors[e_type].append(mem)
        mem['wiki_url'] = wiki_url
    assert new_errors == {}
    print('Incorrect and missing IDs fixed...')

    # Correct 'wiki_url' values
    for mem in key_errors:
        wiki_url = url_from_wikimedia(mem)
        mem['wiki_url'] = wiki_url
    print('Remaining missing URLs added...')

    # Check if all members have 'google_id' and 'wiki_url'
    for mem in members:
        assert mem['google_id'] != None
        assert mem['wiki_url'] != None

    # Batch insert
    batch_insert(
        docs=members,
        db=db,
        col_name='reps',
        _id='_id',
        with_ids=True
    )

if __name__ == '__main__':
    main()