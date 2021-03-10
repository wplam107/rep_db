import pymongo
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from data_acq_functions import Auth
from etl_functions import *

# Maximum batch writes for Firestore
MAX_RESULTS = 500

def main():
    # Configure databases
    config = Auth('./auth/config.ini')
    FIREBASE_CERT = config.get_configs('firebase')[0]
    cred = credentials.Certificate(FIREBASE_CERT)
    firebase_admin.initialize_app(cred)
    f_db = firestore.client() # Firestore database
    m_db = config.config_mongodb() # MongoDB database
    m_coll = m_db['reps']

    # Clean educational data type in database, preparing for unwinding
    clean_edu(m_coll)

    # Paginated results and batch write
    total_docs = m_coll.count_documents({})
    pages = total_docs // MAX_RESULTS
    page_num = 0
    total = 0

    for i in range(pages + 1):
        # Extract and transform from MongoDB
        reps = et_mongo2firestore(m_coll, page_num, MAX_RESULTS)

        # Load to Firestore
        batch = f_db.batch()
        for rep in reps:
            ref = f_db.collection('reps').document(rep['_id'])
            batch.set(ref, rep)
        
        results = batch.commit()
        print('Documents Loaded:', len(results))

        total += len(results)
        page_num += 1

    print(f'*** Total Documents Loaded: {total} ***')
    

if __name__ == '__main__':
    main()