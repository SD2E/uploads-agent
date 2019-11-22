import pymongo
from bson.objectid import ObjectId

from .celery import app
from .config import settings
from . import fsevents

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib.parse import quote_plus


def db_collection(collection=None):
    uri = 'mongodb://{0}:{1}@{2}:{3}/'.format(
        quote_plus(settings['mongodb']['username']
                   ), quote_plus(settings['mongodb']['password']),
        settings['mongodb']['host'], settings['mongodb']['port'])
    client = pymongo.MongoClient(uri)
    db = client[settings['mongodb']['database']]
    if collection is None:
        collection = settings['mongodb']['collection']
    return db[collection]


@app.task
def fsevent_create(event):
    """Store a filesystem event in MongoDB
    """
    dbc = db_collection()
    x_amz_request_id = event.get('Records')[0].get(
        'responseElements').get('x-amz-request-id')
    document = {'body': event,
                'id': x_amz_request_id,
                'state': fsevents.CREATED,
                'history': []
                }
    record_id = dbc.insert_one(document).inserted_id
    return str(record_id)


@app.task
def fsevent_get_key_id(record_id):
    """Get key for the designated filesystem record
    """
    dbc = db_collection()
    _id = ObjectId(record_id)
    record = dbc.find_one({"_id": _id})
    key = record.get('body', {}).get('Key', None)
    event_id = record.get('id', None)
    return (key, event_id)


@app.task
def fsevent_update(event_id_status):
    """Update a filesystem event record with latest status
    """
    event_id = event_id_status[0]
    status = event_id_status[1]
    dbc = db_collection()
    dbc.update_one({'id': event_id}, {'$set': {'state': status}}, upsert=True)
    return (event_id, status)
