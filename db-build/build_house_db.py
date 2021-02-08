from auth import Auth
from db_functions import get_house_ids, get_member_data, member_cleaner, batch_insert_members

# Script
def main():
    auth = Auth('./auth/config.ini')

    # Get ProPublica API Key
    auth.auth_propub()
    api_root, header = auth.get_propub()

    # Get GCP certificate and initialize app
    auth.auth_db()

    # Database
    db = auth.get_db()

    # Create list of member IDs
    ids_116 = get_house_ids(116, header, api_root)
    ids_117 = get_house_ids(117, header, api_root)
    all_ids = list(set(ids_116 + ids_117))
    print('Representative IDs Found...')

    # Generator to get member data
    half = int(len(all_ids)/2)
    members1 = ( get_member_data(member, header, api_root) for member in all_ids[:half] )
    members2 = ( get_member_data(member, header, api_root) for member in all_ids[half:] )

    # Generator to clean member data, must be split in half
    members_insert1 = map(member_cleaner, members1)
    members_insert2 = map(member_cleaner, members2)

    # Batch insert members
    print('Inserting Members...')
    batch_insert_members(members_insert1, db)
    batch_insert_members(members_insert2, db)

if __name__ == '__main__':
    main()