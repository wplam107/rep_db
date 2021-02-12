# Config Reader
import configparser

# Database Connection
import firebase_admin
from firebase_admin import credentials, firestore

# Data
import numpy as np
import pandas as pd
import pickle

# Read config.ini file
config = configparser.ConfigParser()
config.read('.ini')

# Get Google Firebase Auth
GCP_AUTH_PATH = config.get('firebase', 'GCP_AUTH_PATH')
cred = credentials.Certificate(GCP_AUTH_PATH)
app = firebase_admin.initialize_app(cred)

# Instantiate connection to database
db = firestore.client()

# Dictionary to bin degrees
CC_DICT = {
    'Associates': ['AAS', 'AS', 'AA'],
    'Bachelors': ['BS', 'BA', 'SB', 'AB', 'BDiv', 'BBA', 'BEng', 'BM', 'ALB', 'BSN', 'BGS', 'BPA', 'BSBA', 'LLB'],
    'High School': ['HS'],
    'JD': ['JD'],
    'Masters - General': ['MA', 'MS', 'SM', 'MSc', 'MFA', 'MAcc'],
    'Masters - Public': ['MIA', 'MPA', 'MUP', 'MPP', 'MSW', 'MSS', 'MPH', 'MHS'],
    'Masters - Education': ['MEd', 'SYC'],
    'Masters - Law': ['LLM'],
    'Masters - Theology': ['MDiv', 'ThM'],
    'MBA': ['MBA', 'MSEM'],
    'PHD': ['PhD'],
    'Veterinary': ['DVM'],
    'Dental': ['DDS', 'DMD'],
    'MD': ['MD', 'DPM'],
    'PHD - Education': ['EdD'],
    'PHD - Theology': ['DMin'],
    'PHD - Public': ['DPA'],
    'Nursing': ['MSN', 'GrDip'],
}

# Create collection references
reps_ref = db.collection("reps")
edu_ref = db.collection("edu")
votes_ref = db.collection("votes")

# Pull educational and representative data from database
degrees = pd.DataFrame([ doc.to_dict() for doc in edu_ref.get() ])
reps = pd.DataFrame([ doc.to_dict() for doc in reps_ref.get() ])

# Clean degree strings (ex. 'J.D.' -> 'JD')
degrees['degree'] = degrees['degree'].map(lambda x: ''.join(x.split('.')))

# Bin degrees
x = degrees['degree']
cond_list = []
choice_list = []
for k, vs in CC_DICT.items():
    for v in vs:
        cond_list.append(x == v)
        choice_list.append(k)

degrees['degree_group'] = np.select(cond_list, choice_list)

# Convert congresses into set of ints
reps['congresses'] = reps['congresses'].map(lambda x: set([ int(c) for c in x ]))

# Add 'in_office' feature
reps['in_office'] = reps['congresses'].map(set([117]).issubset)

# Replace null values
reps['middle_name'] = np.where(reps['middle_name'].isna(), '', reps['middle_name'])

# Data groupby
institutions = degrees.groupby('_id')['institution'].apply(list)
deg_groups = degrees.groupby('_id')['degree_group'].apply(list)
degs = degrees.groupby('_id')['degree'].apply(list)

# Create merged DataFrame
df = reps[['_id', 'current_party', 'state', 'first_name', 'middle_name', 'last_name', 'dob', 'gender', 'congresses']]
df = df.merge(institutions, how='left', on='_id')
df = df.merge(deg_groups, how='left', on='_id')
data = df.merge(degs, how='left', on='_id')

def main():
    with open('./server/app/data/data.p', 'wb') as f:
        pickle.dump(data, f)

if __name__ == '__main__':
    main()