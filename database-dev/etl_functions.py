import pymongo

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
