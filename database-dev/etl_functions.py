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

def edu_by_state(collection):
    pipeline = [
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
                'bachelors': {'$toInt': {'$or': bachelors}},
                'masters': {'$toInt': {'$or': masters}},
                'doctorate': {'$toInt': {'$or': doctorate}},
                'health': {'$toInt': {'$or': health}},
                'mba': {'$toInt': {'$or': mba}},
                'law': {'$toInt': {'$or': law}},
                'associates': {'$toInt': {'$or': asso}},
                'hs': {'$toInt': {'$or': hs}},
            }
        },
        {
            '$group': {
                '_id': '$state',
                'bachelors': {'$avg': '$bachelors'},
                'masters': {'$avg': '$masters'},
                'doctorate': {'$avg': '$doctorate'},
                'health': {'$avg': '$health'},
                'mba': {'$avg': '$mba'},
                'law': {'$avg': '$law'},
                'associates': {'$avg': '$associates'},
                'hs': {'$avg': '$hs'},
                'count': {'$sum': 1},
            }
        },
        {
            '$sort': {'count': -1}
        },
        {
            '$project': {
                'state': 1,
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