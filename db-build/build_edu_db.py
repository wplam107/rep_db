from auth import Auth
from mediawiki import MediaWiki
from db_functions import find_google_id, get_google_entity, get_wiki_url
from db_functions import get_education, get_alma_mater, clean_education

def main():
    auth = Auth('./auth/config.ini')
    auth.auth_db()
    db = auth.get_db()
    ref = db.collection("reps")
    auth.auth_gcp()
    gcp_key = auth.get_gcp_key()

    # Retrieve all reps
    query = ref.where("_id", "!=", "").select(["_id", "google_id", "first_name", "middle_name", "last_name"]).stream()
    reps = [ doc.to_dict() for doc in query ]

    # Find and assign Google Entity IDs for reps with missing google_ids
    for rep in reps:
        if rep['google_id'] == None:
            rep['google_id'] = find_google_id(rep, gcp_key)
    print('Found Missing Google IDs...')

    # Get Wikipedia URLs for reps
    for rep in reps:
        rep['wiki_url'], rep['error'] = get_wiki_url(rep, gcp_key)
    print('Found Wikipedia URLs...')

    # Check reps with errors
    errors = {}
    for rep in reps:
        error = rep['error']
        if error == None:
            pass
        else:
            e_type = type(error)
            if e_type not in errors.keys():
                errors[e_type] = []
            
            errors[e_type].append(rep)

    # Use new Google Entity ID to get Wikipedia URL
    for rep in errors[IndexError]:
        rep['google_id'] = find_google_id(rep, gcp_key)
        rep['wiki_url'], rep['error'] = get_wiki_url(rep, gcp_key)
    print('Fixed IndexErrors...')

    # Get Wikipedia URLs
    wikipedia = MediaWiki()
    for rep in errors[KeyError]:
        name = get_google_entity(rep, gcp_key)['itemListElement'][0]['result']['name']
        p = wikipedia.page(f'{name} politician')
        rep['wiki_url'] = p.url
        rep['error'] = None
    print('Fixed KeyErrors...')

    # Get education from Wikipedia with error saving
    errors = {}
    for rep in reps:
        wiki_url = rep['wiki_url']
        rep['education'], rep['error'] = get_education(wiki_url)
        if rep['error'] == None:
            pass
        else:
            e_type = type(rep['error'])
            if e_type not in errors.keys():
                errors[e_type] = []
            
            errors[e_type].append(rep)
    print('Webscraped Education from Wikipedia...')

    # Reassign errors
    errors = errors[AttributeError]

    # No tertiary education
    no_edus = []
    for rep in errors:
        rep['education'], rep['error'] = get_alma_mater(rep)
        if rep['error'] != None:
            no_edus.append(rep)
    print('Fixed AtrributeErrors...')

    # Remove error keys from rep dictionaries
    for rep in reps:
        del rep['error']

    # Clean education
    for rep in reps:
        rep['education'] = clean_education(rep)

    # Batch update wiki_url and google_id
    batch = db.batch()
    total = 0
    insert_len = 0
    batch_num = 1
    for rep in reps:
        insert_ref = db.collection("reps").document(rep['_id'])
        up_dict = {
            'google_id': rep['google_id'],
            'wiki_url': rep['wiki_url'],
        }
        batch.update(insert_ref, up_dict)
        insert_len += 1
        total += 1
        if insert_len > 200:
            batch.commit()
            print(f'{insert_len} reps updated in batch #{batch_num}')
            insert_len = 0
            batch_num += 1
            
    batch.commit()
    print(f'{insert_len} reps updated in batch #{batch_num}')
    print(f'{total} reps updated in total')

    # Batch insert educational background data
    batch = db.batch()
    total = 0
    insert_len = 0
    batch_num = 1
    for rep in reps:
        for edu in rep['education']:
            insert_ref = db.collection("edu").document()
            data = {
                '_id': rep['_id'],
                'degree': edu[0],
                'institution': edu[1]
            }
            batch.set(insert_ref, data)
            insert_len += 1
            total += 1
            if insert_len > 399:
                batch.commit()
                print(f'{insert_len} degrees inserted in batch #{batch_num}')
                insert_len = 0
                batch_num += 1

    batch.commit()
    print(f'{insert_len} degrees inserted in batch #{batch_num}')
    print(f'{total} degrees inserted in total')

if __name__ == '__main__':
    main()