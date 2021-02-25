import configparser
import pymongo
from pymongo import InsertOne

from googleapiclient.discovery import build
from mediawiki import MediaWiki

from data_acq_functions import get_house_ids, get_rep_data

# Get config file
config = configparser.ConfigParser()
config.read('../database-dev/auth/config.ini')

# Get ProPublica config
PROPUBLICA_KEY = config.get('propublica', 'PROPUBLICA_API_KEY')
API_ROOT = config.get('propublica', 'API_ROOT')
PROPUBLICA_HEADER = {'X-API-Key': f'{PROPUBLICA_KEY}'}

# Get API key for GKG
GKG_API_KEY = config.get('gcpkeys', 'GKG_API_KEY')
GKG = config.get('gcpkeys', 'GKG')
GKG_VERSION = config.get('gcpkeys', 'GKG_VERSION')

# Instantiate service connection
service = build(GKG, GKG_VERSION, developerKey=GKG_API_KEY)
entities = service.entities()

# Instantiate wikipedia object
wikipedia = MediaWiki()

# Get MongoDB config
MONGO_LOCAL = config.get('mongodb', 'MONGO_LOCAL')
MONGO_DB = config.get('mongodb', 'MONGO_DB')
client = pymongo.MongoClient(MONGO_LOCAL)

# Connect to database
db = client.get_database(MONGO_DB)

def main():
    # Instantiate connection to collection
    collection = db['reps']

    # Get all house members of the 117th congress
    members = get_house_ids(117, API_ROOT, PROPUBLICA_HEADER)

    # Insert statements
    inserts = []
    for member in members:
        data = get_rep_data(member, API_ROOT, PROPUBLICA_HEADER, entities, wikipedia)
        inserts.append(InsertOne(data))

    # Bulk write to collection
    result = collection.bulk_write(inserts)

    print(result.bulk_api_result)

if __name__ == '__main__':
    main()
