import couchdb
from Karten.settings import COUCHDB_SERVERS, COUCHDB_CREDENTIALS


server_name = 'Karten'

def couchdb_instance():
    server_info = COUCHDB_SERVERS[server_name]
    server_credentials = COUCHDB_CREDENTIALS[server_name]
    authed_url = "%s://%s:%s@%s:%s/" % (server_info['url_scheme'], 
            server_credentials['username'], 
            server_credentials['password'],
            server_info['host'],
            server_info['port'])
    instance = couchdb.Server(url=authed_url)
    return instance

def unauthed_couch_url():
    server_info = COUCHDB_SERVERS[server_name]
    unauthed_url = "%s://%s:%s/" % (server_info['url_scheme'], server_info['host'], server_info['port'])
    return unauthed_url
