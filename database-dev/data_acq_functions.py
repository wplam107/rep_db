import requests
import functools
import re
import googleapiclient

########################
# ProPublica Functions #
########################

def get_house_ids(congress, api_root, header):
    '''
    Function to retrieve all member IDs for a particular house in congress
    '''
    
    call_string = api_root + f'{congress}/house/members.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]['members']
    member_ids = [ member['id'] for member in result ]
    
    return member_ids

def get_mem_json(member, api_root, header):
    '''
    Function to retrieve JSON of particular member
    '''

    call_string = api_root + f'members/{member}.json'
    r = requests.get(call_string, headers=header)
    result = r.json()['results'][0]
    
    return result

def clean_role(role):
    '''
    Helper function to pull relevant role data
    '''

    role_dict = {
        'congress': role['congress'],
        'state': role['state'],
        'party': role['party'],
        'district': role['district'],
        'committees': [
            {'name': comm['name'], 'code': comm['code']}
            for comm in role['committees']
        ],
        'subcommittees': [
            {'name': comm['name'], 'code': comm['code'], 'parent_code': comm['parent_committee_id']}
            for comm in role['subcommittees']
        ]
    }
    
    return role_dict

def get_member(member_id, api_root, header):
    '''
    Function to get house member data as python dictionary
    '''
    
    member = get_mem_json(member_id, api_root, header)
    current = member['roles'][0]
    fec_id = current['fec_candidate_id'] # Most recent FEC candidate ID
    state = current['state'] # Most recent state represented
    
    mem_dict = {
        '_id': member['id'],
        'first_name': member['first_name'],
        'middle_name': member['middle_name'],
        'last_name': member['last_name'],
        'dob': member['date_of_birth'],
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
        'roles': [ clean_role(role) for role in member['roles'] ]
    }
    
    return mem_dict


################################################
# Google Knowledge Graph / MediaWiki Functions #
################################################

# Wrapper for error logging
def error_logging(func):
    @functools.wraps(func)
    def wrapper_error(*args):
        data = None
        error = None
        try:
            data = func(*args)
        except Exception as e:
            error = type(e)
        return data, error
    return wrapper_error

@error_logging
def get_wiki_url(rep, entities):
    '''
    Function to get wikipedia URL from Google Knowledge Graph with Google entity ID query
    '''
    
    _id = rep['google_id']
    r = entities.search(ids=_id).execute()
    result = r['itemListElement'][0]['result']
    wiki_url = result['detailedDescription']['url']
    
    return wiki_url

@error_logging
def gkg_search(rep, entities):
    '''
    Function to get google_id and wikipedia URL from Google Knowledge Graph with search term query
    '''
    
    query = f"{rep['first_name']} {rep['last_name']} politician"
    r = entities.search(query=query).execute()
    result = r['itemListElement'][0]['result']
    _id = result['@id']
    gid = re.search('(?<=:).*', _id)[0]
    try:
        wiki_url = result['detailedDescription']['url']
    except:
        wiki_url = None
    
    return gid, wiki_url

@error_logging
def mediawiki_search(rep, wikipedia):
    '''
    Function to get wikipedia URL from MediaWiki
    '''
    
    query = f"{rep['first_name']} {rep['last_name']} politician"
    wiki_url = wikipedia.page(query).url
    
    return wiki_url

def get_rep_data(member_id, api_root, header, entities, wikipedia):
    '''
    Function to retrieve data for US Representative
    '''
    
    # Retrieve from ProPublica representative JSON
    rep = get_member(member_id, api_root, header) # Outside function
    
    # Initial attempt to retrieve wikipedia URL
    wiki_url, error = get_wiki_url(rep, entities) # Outside function
    rep['wiki_url'] = wiki_url
    
    # Missing or wrong google_id in ProPublica data
    if (error == googleapiclient.errors.HttpError) or (error == IndexError):
        data, error = gkg_search(rep, entities) # Outside function
        gid = data[0]
        wiki_url = data[1]
        rep['google_id'] = gid
        rep['wiki_url'] = wiki_url
        
    # Missing wikipedia URL in Google Knowledge Graph
    if (error == KeyError) or (rep['wiki_url'] == None):
        wiki_url, error = mediawiki_search(rep, wikipedia) # Outside function
        rep['wiki_url'] = wiki_url
        
    return rep

