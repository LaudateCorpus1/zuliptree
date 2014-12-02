from pymongo import MongoClient
def get_db_client():
    with open('mongo-pass.conf', 'r') as f:
        mpass = f.read().strip()
        client = MongoClient('mongodb://chase:{}@104.131.112.57'.format(mpass))
        return client
    exit("Could not connect to the dababase!")
