import base64

# TODO Implement at least trivial encryption

def decode_authn_string(authn_string):
    """Decodes a hexadecimal authentication string into a MongoDB connnection URI"""
    return base64.urlsafe_b64decode(authn_string.encode('utf-8')).decode('utf-8')

def encode_connection_string(conn_string):
    """Encodes a MongoDB connnection URI as a hexadecimal authentication string"""
    b = bytes(conn_string.encode('utf-8'))
    return base64.urlsafe_b64encode(b).decode('utf-8')
