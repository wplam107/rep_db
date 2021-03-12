import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from data_acq_functions import Auth
from etl_functions import gender_by_state, party_by_state

def main():
    # Config databases
    config = Auth('./auth/config.ini')
    m_db = config.config_mongodb()
    m_coll = m_db['reps']
    FIREBASE_CERT = config.get_configs('firebase')[0]
    cred = credentials.Certificate(FIREBASE_CERT)
    firebase_admin.initialize_app(cred)
    f_db = firestore.client()
    gen_coll = f_db.collection('state_gender')
    party_coll = f_db.collection('state_party')
    batch = f_db.batch()

    # ETL gender by state
    states = gender_by_state(m_coll)
    for state in states:
        ref = gen_coll.document(state['_id'])
        batch.set(ref, state)
    results = batch.commit()
    print('Gender by State Docs Loaded:', len(results))

    # ETL party by state
    states = party_by_state(m_coll)
    for state in states:
        ref = party_coll.document(state['_id'])
        batch.set(ref, state)
    results = batch.commit()
    print('Party by State Docs Loaded:', len(results))

if __name__ == '__main__':
    main()
