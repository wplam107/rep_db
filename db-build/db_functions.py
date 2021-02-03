import requests
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

def get_house_ids(congress, header, api_root):
    '''
    Function to get house members' ProPublica ID by congress number
    '''

    call_string = api_root + f'{congress}/house/members.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]['members']
    member_ids = [ member['id'] for member in result ]
    
    return member_ids

def get_member_data(member, header, api_root):
    '''
    Function to get house member's data
    '''
    
    call_string = api_root + f'members/{member}.json'
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
    congresses = [ role['congress'] for role in roles ]
    
    mem_dict = {
        '_id': member['id'],
        'first_name': member['first_name'],
        'middle_name': member['middle_name'],
        'last_name': member['last_name'],
        'dob': to_date(member['date_of_birth']),
        'gender': member['gender'],
        'current_party': member['current_party'],
        'google_id': member['google_entity_id'],
        'votesmart_id': member['votesmart_id'],
        'govtrack_id': member['govtrack_id'],
        'cspan_id': member['cspan_id'],
        'crp_id': member['crp_id'],
        'fec_id': fec_id,
        'congresses': congresses,   
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

def get_roll_call_vote(congress, session, roll_call_number, api_root, header):
    '''
    Function to get singular roll call vote
    '''
    
    call_string = api_root + f'{congress}/house/sessions/{session}/votes/{roll_call_number}.json'
    r = requests.get(call_string, headers=header)
    
    # Ignore nominations, quorum, and non-bill actions
    try:
        result = r.json()['results']['votes']['vote']
        if (result['bill'] == {}) or (result['bill']['number'] == 'QUORUM'):
            return None
        else:
            return result
        
    except:
        return None

def rc_clean(rc_vote):
    '''
    Function to keep relevent information from roll call
    '''

    if rc_vote != None:
        bill = rc_vote['bill']
        vote_dict = {
            'congress': rc_vote['congress'],
            'session': rc_vote['session'],
            'roll_call': rc_vote['roll_call'],
            'bill_id': bill['bill_id'],
            'api_call_id': ''.join(bill['number'].split('.')).lower(),
            'title': bill['title'],
            'description': rc_vote['description'],
            'date': to_date(rc_vote['date']),
            'result': rc_vote['result'],
            'yes': [],
            'no': [],
            'not voting': [],
            'present': [],
            'speaker': [],
        }
        for mem in rc_vote['positions']:
            mem_id = mem['member_id']
            pos = mem['vote_position'].lower()
            vote_dict[pos].append(mem_id)
    
    else:
        vote_dict = None
        
    return vote_dict

def batch_insert_rc(db, members):
    '''
    Function to batch insert roll call votes
    '''

    batch = db.batch()
    mem_num = 0
    b_num = 1
    total = 0
    for mem in members:
        if mem != None:
            c = mem['congress']
            s = mem['session']
            r = mem['roll_call']
            _id = f'{c}_{s}_{r}'
            insert_ref = db.collection("votes").document(_id)
            batch.set(insert_ref, mem)
            mem_num += 1
            total += 1
            if mem_num > 399:
                batch.commit()
                print(f'{mem_num} bills inserted in batch #{b_num}')
                mem_num = 0
                b_num += 1
                batch = db.batch()
    
    batch.commit()
    print(f'{mem_num} bills inserted in batch #{b_num}')
    print(f'Total inserted: {total}')