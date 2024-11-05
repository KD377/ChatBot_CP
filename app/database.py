from pymongo import MongoClient

def get_collection():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['dziennik_ustaw']
    collection = db['laws']
    return collection
