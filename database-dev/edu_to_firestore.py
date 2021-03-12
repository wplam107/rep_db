import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from data_acq_functions import Auth
from etl_functions import edu_by_state

def main():
    # Config databases
    config = Auth('./auth/config.ini')
    m_db = config.config_mongodb()
    m_coll = m_db['reps']
    FIREBASE_CERT = config.get_configs('firebase')[0]
    cred = credentials.Certificate(FIREBASE_CERT)
    firebase_admin.initialize_app(cred)
    f_db = firestore.client()
    f_coll = f_db.collection('state_edu')

    # Extract from MongoDB
    states = edu_by_state(m_coll)
    
    # Load to Firestore
    batch = f_db.batch()
    for state in states:
        ref = f_coll.document(state['_id'])
        batch.set(ref, state)

    results = batch.commit()
    print('Docs loaded:', len(results))


if __name__ == '__main__':
    main()