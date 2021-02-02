import configparser
import firebase_admin
from firebase_admin import credentials, firestore
from db_functions import get_house_ids, get_member_data, member_cleaner, batch_insert_members

# Script
def main():
    # Read config file
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Get ProPublica API Key
    PROPUBLICA_API_KEY = config.get('propublica', 'PROPUBLICA_API_KEY')
    API_ROOT = 'https://api.propublica.org/congress/v1/'
    header = {'X-API-Key': f'{PROPUBLICA_API_KEY}'}

    # Get GCP certificate and initialize app
    GCP_AUTH_PATH = config.get('firebase', 'GCP_AUTH_PATH')
    cred = credentials.Certificate(GCP_AUTH_PATH)
    app = firebase_admin.initialize_app(cred)

    # Database
    db = firestore.client()

    # Create list of member IDs
    ids_116 = get_house_ids(116, header, API_ROOT)
    ids_117 = get_house_ids(117, header, API_ROOT)
    all_ids = list(set(ids_116 + ids_117))

    # Generator to get member data
    half = int(len(all_ids)/2)
    members1 = ( get_member_data(member, header, API_ROOT) for member in all_ids[:half] )
    members2 = ( get_member_data(member, header, API_ROOT) for member in all_ids[half:] )

    # Generator to clean member data, must be split in half
    members_insert1 = map(member_cleaner, members1)
    members_insert2 = map(member_cleaner, members2)

    # Batch insert members
    batch_insert_members(members_insert1, db)
    batch_insert_members(members_insert2, db)

if __name__ == '__main__':
    main()