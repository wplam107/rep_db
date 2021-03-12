import pymongo
import us

def clean_edu(collection):
    '''
    Function to maintain consistent educational background data types
    (i.e. None-> [['HS', 'High School']])
    '''

    results_1 = collection.update_many(
        {'education': None},
        {'$set': {'education': [['HS', 'High School']]}}
    )
    results_2 = collection.update_many(
        {'education': []},
        {'$set': {'education': [['HS', 'High School']]}}
    )
    total = results_1.modified_count + results_2.modified_count
    print(f'Documents updated: {total}')

def et_mongo2firestore(collection, page_num, max_results):
    '''
    Extract, transform stage of MongoDB to Firestore
    '''

    match_stage = {
        '$match': {'in_office': True}
    }
    fields_stage = {
        '$addFields': {
            'name': {'$concat': ['$first_name',' ', '$last_name']},
            'district': {'$arrayElemAt': ['$roles.district', 0]},
        }
    }
    unwind_stage = {
        '$unwind': '$education'
    }
    group_stage = {
        '$group': {
            '_id': '$_id',
            'name': {'$first': '$name'},
            'dob': {'$first': '$dob'},
            'gender': {'$first': '$gender'},
            'party': {'$first': '$current_party'},
            'state': {'$first': '$state'},
            'district': {'$first': {'$convert': {'input': '$district', 'to': 'int', 'onError': '$district'}}},
            'wikipedia': {'$first': '$wiki_url'},
            'degrees': {'$push': {'$arrayElemAt': ['$education', 0]}},
            'education': {'$push': {'$arrayElemAt': ['$education', 1]}},
        }
    }
    sort_stage = {
        '$sort': {'_id': 1}
    }
    skip_stage = {
        '$skip': page_num * max_results
    }
    limit_stage = {
        '$limit': max_results
    }
    pipeline = [
        match_stage, fields_stage, unwind_stage, group_stage,
        sort_stage, skip_stage, limit_stage
    ]
    results = collection.aggregate(pipeline)
    reps = [ rep for rep in results ]

    return reps

def edu_by_state(collection):
    '''
    Function to get proportions of reps with educational degrees
    '''

    # Bin degrees
    degree_dict = {
        'Bachelors': [
            'BS', 'BA', 'AB', 'BPA', 'BBA', 'ALB', 'LLB', 'BDIV',
            'BSFS', 'BPA', 'BSN', 'BGS'
        ],
        'Masters': [
            'MPA', 'MA', 'MSW', 'MS', 'MPP', 'MDIV', 'THM', 'MUP',
            'MHS', 'SYC', 'GRCERT', 'MPHIL', 'MIA', 'MSS', 'MPH',
            'MACC', 'MFA', 'MED', 'MPH', 'MSEM', 'MSC'
        ],
        'Doctorate': ['PHD', 'DPA', 'EDD', 'PHARMD', 'DMIN', 'DPHIL'],
        'MBA': ['MBA'],
        'Med': ['MD', 'DPM'],
        'Vet': ['DVM'],
        'Nur': ['GRDIP', 'MSN'],
        'Den': ['DDS', 'DMD'],
        'Law': ['JD', 'LLM'],
        'HS': ['HS'],
        'Associates': ['AA', 'AAS', 'AS']
    }
    degree_dict['Health'] = degree_dict['Med'] + degree_dict['Vet'] + degree_dict['Nur'] + degree_dict['Den']
    
    # Define states to match (i.e. exclude Virgin Islands)
    state_abbrs = [ state.abbr for state in us.states.STATES ] + ['DC']

    pipeline = [
        {
            '$match': {'$expr': {'$in': ['$state', state_abbrs]}}
        },
        {
            '$unwind': '$education'
        },
        {
            '$group': {
                '_id': '$_id',
                'state': {'$first': '$state'},
                'degrees': {'$push': {'$arrayElemAt': ['$education', 0]}},
            }
        },
        {
            '$addFields': {
                k.lower(): {'$toInt': {'$or' :[ {'$in': [v, '$degrees']} for v in degree_dict[k] ]}}
                for k in degree_dict.keys()
            }
        },
        {
            '$group': {
                '_id': '$state',
                'bachelors': {'$sum': '$bachelors'},
                'masters': {'$sum': '$masters'},
                'doctorate': {'$sum': '$doctorate'},
                'health': {'$sum': '$health'},
                'mba': {'$sum': '$mba'},
                'law': {'$sum': '$law'},
                'associates': {'$sum': '$associates'},
                'hs': {'$sum': '$hs'},
                'count': {'$sum': 1},
            }
        },
        {
            '$sort': {'count': -1}
        },
        {
            '$project': {
                'bachelors': {'$round': ['$bachelors', 4]},
                'masters': {'$round': ['$masters', 4]},
                'doctorate': {'$round': ['$doctorate', 4]},
                'health': {'$round': ['$health', 4]},
                'mba': {'$round': ['$mba', 4]},
                'law': {'$round': ['$law', 4]},
                'associates': {'$round': ['$associates', 4]},
                'hs': {'$round': ['$hs', 4]},
                'count': 1,
            }
        }
    ]
    results = collection.aggregate(pipeline)
    states = [ state for state in results ]

    return states

def party_by_state(collection):
    state_abbrs = [ state.abbr for state in us.states.STATES ] + ['DC']

    pipeline = [
        {
            '$match': {'$expr': {'$in': ['$state', state_abbrs]}}
        },
        {
        '$project': {
            '_id': 0,
            'state': 1,
            'R': {'$toInt': {'$eq': ['$current_party', 'R']}},
            'D': {'$toInt': {'$eq': ['$current_party', 'D']}},
            'I': {'$toInt': {'$eq': ['$current_party', 'I']}},
        }  
        },
        {
            '$group': {
                '_id': '$state',
                'R': {'$sum': '$R'},
                'D': {'$sum': '$D'},
                'I': {'$sum': '$I'},
            }
        }
    ]

    results = collection.aggregate(pipeline)
    states = [ state for state in results ]

    return states

def gender_by_state(collection):
    state_abbrs = [ state.abbr for state in us.states.STATES ] + ['DC']

    pipeline = [
        {
            '$match': {'$expr': {'$in': ['$state', state_abbrs]}}
        },
        {
            '$project': {
                '_id': 0,
                'state': 1,
                'M': {'$toInt': {'$eq': ['$gender', 'M']}},
                'F': {'$toInt': {'$eq': ['$gender', 'F']}},
            }
        },
        {
            '$group': {
                '_id': '$state',
                'M': {'$sum': '$M'},
                'F': {'$sum': '$F'},
            }
        },
    ]

    states = [ state for state in collection.aggregate(pipeline) ]

    return states