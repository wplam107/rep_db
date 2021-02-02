import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

def get_house_ids(congress, header, API_ROOT):
    '''
    Function to get house members' ProPublica ID by congress number
    '''

    call_string = API_ROOT + f'{congress}/house/members.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]['members']
    member_ids = [ member['id'] for member in result ]
    
    return member_ids

def get_member_data(member, header, API_ROOT):
    '''
    Function to get house member's data
    '''
    
    call_string = API_ROOT + f'members/{member}.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]
    
    return result

def to_date(s):
    date = datetime.strptime(s, '%Y-%m-%d')
    return date

def member_cleaner(member):
    '''
    Function to keep relevent information on congress member
    '''
    
    roles = member['roles']
    roles.sort(key=lambda x: x['congress'], reverse=True)
    fec_id = roles[0]['fec_candidate_id'] # Most recent FEC candidate ID
    
    mem_dict = {
        '_id': member['id'],
        'bio': {
            'first_name': member['first_name'],
            'middle_name': member['middle_name'],
            'last_name': member['last_name'],
            'dob': to_date(member['date_of_birth']),
            'gender': member['gender'],
            'current_party': member['current_party'],
        },
        'activity': {
            'last_updated': to_date(member['last_updated'][:10]), # Ignore time
            'in_office': member['in_office'],
        },
        'other_ids': {
            'google_id': member['google_entity_id'],
            'votesmart_id': member['votesmart_id'],
            'govtrack_id': member['govtrack_id'],
            'cspan_id': member['cspan_id'],
            'crp_id': member['crp_id'],
            'fec_id': fec_id,
        },
        'roles': member['roles'],   
    }
    
    return mem_dict

def batch_insert_members(members, db):
    '''
    Function to batch insert house members into database
    '''
    
    batch = db.batch()
    members_len = 0
    for member in members:
        _id = member['_id']
        insert_ref = db.collection("reps").document(f"{_id}")
        batch.set(insert_ref, member)
        members_len += 1
            
    batch.commit()
    
    batch_len = len(batch.write_results)
    f_string = f'Batch Length: {batch_len}, Members Length: {members_len}'
    assert batch_len == members_len, f_string
    
    print(f'{batch_len} members inserted')