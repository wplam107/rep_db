import pymongo

def clean_edu(collection):
    '''
    Function to maintain consistent educational background data types
    (i.e. None-> [['HS', 'High School']])
    '''

    results = collection.update_many(
        {'education': None},
        {'$set': {'education': [['HS', 'High School']]}}
    )
    print(f'Documents updated: {results.modified_count}')

def reps_paginated(collection, page_num, limit):
    '''
    Return paginated reps
    '''

    skip = page_num * limit
    results = collection.find({}).sort('_id', pymongo.ASCENDING).skip(skip).limit(limit)
    reps = [ rep for rep in results ]

    return reps

def state_reps(state):
    '''
    Function to get reps by state from MongoDB
    '''

    match = {
        '$match': {
            'in_office': True,
            'state': state,
        }
    }
    add_fields = {
        '$addFields': {
            'name': {'$concat': ['$first_name',' ', '$last_name']},
            'district': {'$arrayElemAt': ['$roles.district', 0]},
        }
    }
    unwind = {
        '$unwind': '$education'
    }
    group = {
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
    sort = {
        '$sort': {
            'district': 1,
        }
    }
    
    pipeline = [match, add_fields, unwind, group, sort]
    results = collection.aggregate(pipeline)
    reps = [ rep for rep in results ]
    
    return reps