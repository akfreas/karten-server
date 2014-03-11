from sqlalchemy import create_engine
import settings
engine = create_engine('postgresql:///%s:%s@%s:%s/karten' % (settings.PSQL_USERNAME, settings.PSQL_PASSWORD, settings.PSQL_SERVER, settings.PSQL_PORT))

