from auth import Auth
from db_functions import get_roll_call_vote, rc_clean, batch_insert_rc

def main():
    auth = Auth('config.ini')

    # Get ProPublica API Key
    auth.auth_propub()
    api_root, header = auth.get_propub()

    # Get GCP certificate and initialize app
    auth.auth_db()

    # Database
    db = auth.get_db()

    # Roll calls from 1st and 2nd sessions of 116th congress
    rc_116_1 = range(1, 702) # 701 roll calls
    rc_116_2 = range(1, 254) # 253 roll calls

    # Roll calls from 1st session of 117th congress (as of 2021-02-02)
    rc_117_1 = range(1, 19) # 18 roll calls

    # Generators for batch insert
    votes_116_1 = ( rc_clean(get_roll_call_vote(116, 1, rc, api_root, header)) for rc in rc_116_1 )
    votes_116_2 = ( rc_clean(get_roll_call_vote(116, 2, rc, api_root, header)) for rc in rc_116_2 )
    votes_117_1 = ( rc_clean(get_roll_call_vote(117, 1, rc, api_root, header)) for rc in rc_117_1 )

    # Batch insert
    batch_insert_rc(db, votes_116_1)
    batch_insert_rc(db, votes_116_2)
    batch_insert_rc(db, votes_117_1)

    print('Inserts complete')

if __name__ == '__main__':
    main()