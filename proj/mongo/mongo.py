from bson.binary import UUID_SUBTYPE, OLD_UUID_SUBTYPE
from datacatalog import settings
from pymongo import MongoClient, ReturnDocument, ASCENDING
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from .encodeauthn import decode_authn_string

try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib.parse import quote_plus

def get_mongo_uri(mongodct={}):
    uri = None
    if 'username' in mongodct:
        uri = "mongodb://%s:%s@%s:%s/%s" % (quote_plus(mongodct.get('username', settings.MONGODB_USERNAME)),
                                            quote_plus(mongodct.get('password', settings.MONGODB_USERNAME)),
                                            mongodct.get('host', settings.MONGODB_HOST),
                                            mongodct.get('port', settings.MONGODB_PORT),
                                            mongodct.get('auth_source', settings.MONGODB_AUTH_DATABASE))
    elif 'authn' in mongodct:
        # base64 encoded connection string suitable for setting as a container secret
        uri = decode_authn_string(mongodct.get('authn', settings.MONGODB_AUTHN))
    else:
        raise ValueError('Unable to parse MongoDB connection details')
    return uri

def db_connection(mongodct):
    """Get an active MongoDB connection

    Supports two formats for dict:settings

    ---
    username: <uname>
    password: <pass>
    host: <host>
    port: <port>
    database: <database>

    OR

    ---
    authn: <base64.urlsafe_b64encode(connection_string)>
    database: <database>
    """
    try:
        uri = get_mongo_uri(mongodct)
        client = MongoClient(uri, appname='datacatalog', connect=False)
        db = client[mongodct.get('database', settings.MONGODB_DATABASE)]
        return db
    except Exception as exc:
        raise ConnectionFailure('Unable to connect to database', exc)
