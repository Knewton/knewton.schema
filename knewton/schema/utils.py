import types
import MySQLdb

def db_connect(config, override_kwargs=None, **kwargs):

	if override_kwargs:
		kwargs = override_kwargs

	if type(config) in types.StringTypes:
		config = KnewtonConfig.fetch_config(config)

	if config.has_key('database'):
		val = config['database']
		if type(val) == dict:
			config = val
	host = __get_field(config, "host")
	db = __get_field(config, "database")
	user = __get_field(config, "username")
	passwd = __get_field(config, "password")
	return MySQLdb.connect(host=host, db=db, user=user, passwd=passwd, **kwargs)

