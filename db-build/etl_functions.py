# Webscraping and API calls
import requests
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from mediawiki import MediaWiki

# Utils
import re
from datetime import datetime
from decorators import error_logging


########################
# ProPublica functions #
########################

def get_house_ids(congress, API_ROOT, header):
    '''
    Function to get house members' ProPublica ID by congress number
    '''

    call_string = API_ROOT + f'{congress}/house/members.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]['members']
    member_ids = [ member['id'] for member in result ]
    
    return member_ids

def get_member_data(member, API_ROOT, header):
    '''
    Function to get house member's data
    '''
    
    call_string = API_ROOT + f'members/{member}.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]
    
    return result

def member_cleaner(member):
    '''
    Function to keep relevent information on congress member
    '''
    
    roles = member['roles']
    roles.sort(key=lambda x: x['congress'], reverse=True)
    fec_id = roles[0]['fec_candidate_id'] # Most recent FEC candidate ID
    state = roles[0]['state'] # Most recent state served
    congresses = [ role['congress'] for role in roles ]
    date = datetime.strptime(member['date_of_birth'], '%Y-%m-%d')
    
    mem_dict = {
        '_id': member['id'],
        'first_name': member['first_name'],
        'middle_name': member['middle_name'],
        'last_name': member['last_name'],
        'dob': date,
        'gender': member['gender'],
        'current_party': member['current_party'],
        'state': state,
        'google_id': member['google_entity_id'],
        'votesmart_id': member['votesmart_id'],
        'govtrack_id': member['govtrack_id'],
        'cspan_id': member['cspan_id'],
        'crp_id': member['crp_id'],
        'fec_id': fec_id,
        'in_office': member['in_office'],
        'congresses': congresses,   
    }
    
    return mem_dict


#######################
# Firestore functions #
#######################

def batch_insert(docs, db, col_name, _id='id', with_ids=True):
    '''
    Function to batch write to Firestore
    '''
    
    print(f'Writing data to {col_name} collection...')
    batch = db.batch()
    batch_len = 0
    batch_num = 0
    total = 0
    for doc in docs:
        if with_ids:
            insert_id = f'{doc[_id]}'
        else:
            insert_id = None
        
        ref = db.collection(col_name).document(insert_id)
        batch.set(ref, doc)
        batch_len += 1
        total += 1
        
        if batch_len > 499:
            batch.commit()
            print(f'Batch {batch_num} Inserted')
            print(f'Inserts: {len(batch.write_results)}')
            batch_len = 0
            batch_num += 1
        
    batch.commit()
    print(f'Batch {batch_num} Inserted')
    print(f'Inserts: {len(batch.write_results)}')
    print(f'***Total Inserts: {total}')


###############
# Google APIs #
###############

def kg_id(mem, entities):
    '''
    Function to search by Google Entity ID in Google Knowledge Graph
    '''
    
    _id = mem['google_id']
    r = entities.search(ids=_id).execute()
    result = r['itemListElement'][0]['result']
    return result

@error_logging
def get_wikipedia(mem, entities):
    '''
    Get Wikipedia page of US Representative
    '''
    
    result = kg_id(mem, entities)
    wiki_url = result['detailedDescription']['url']
    return wiki_url

def kg_search(mem, entities):
    '''
    Function to find Google Entity by search
    '''
    
    data = [
        mem['first_name'],
        mem['last_name'],
        'politician'
    ]
    query = ' '.join(data)
    r = entities.search(query=query).execute()
    result = r['itemListElement'][0]['result'] # Return top result
    return result

@error_logging
def get_google_id(mem, entities):
    '''
    Get Google Entity ID via Google Knowledge Graph search
    '''
    
    result = kg_search(mem, entities)
    s = result['@id']
    _id = re.search('(?<=:).*', s)[0]
    return _id


#######################
# WikiMedia functions #
#######################

def url_from_wikimedia(mem):
    '''
    Function to get Wikipedia URL of Representative from WikiMedia search
    '''
    
    wikipedia = MediaWiki()
    name = f"{mem['first_name']} {mem['last_name']} politician"
    wiki_url = wikipedia.page(name).url
    return wiki_url