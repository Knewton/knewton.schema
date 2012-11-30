# vim:foldmethod=indent
import warnings
warnings.filterwarnings('ignore', '.*the sets module is deprecated.*', DeprecationWarning, 'MySQLdb')
import os
from optparse import OptionParser
from knewton.config import *
from knewton.schema.version_1 import SchemaVersion1
from knewton.schema.utils import db_connect

def up(conn, table_base):
	table_base(conn).up()

def down(conn, table_base, ver):
	table_base(conn).down(ver)

def report(conn, table_base):
	ver = table_base(conn).check_version()
	if type(ver) == type (()):
		vl = []
		pstr = "Versions: "
		for vn in ver:
			vl.append(str(vn[0]))
		pstr += ", ".join(vl)
		print pstr
	else:
		print "version:", ver

def execute(table_base, default, schema=None):
	parser = optionParser()
	(options, args) = parser.parse_args()
	config = None
	if options.config:
		config = options.config
	yf = fetch_knewton_config(default, config)
	if schema:
		yf['database']['database'] = schema
	conn = db_connect(yf['database'])
	try:
		if options.ver:
			report(conn, table_base)
		elif options.down:
			down(conn, table_base, int(options.down))
		else:
			up(conn, table_base)
	finally:
		conn.close()

def optional_arg_callback(arg_default):
	"""Taken from http://stackoverflow.com/questions/1229146/parsing-empty-options-in-python"""
	def func(option, opt_str, value, parser):
		if parser.rargs and not parser.rargs[0].startswith('-'):
			val = parser.rargs[0]
			parser.rargs.pop(0)
		else:
			val = arg_default
		setattr(parser.values, option.dest, val)
	return func

def optionParser():
	usage = "usage: %prog [options]\n\nChecks and updates the table_base to this verison"
	parser = OptionParser(usage=usage)

	parser.add_option("-u", "--up", action="store_true", dest="up", help="update to the latest table_base")
	# NOTE: The parameter in the following function call must me "0" and not 0, otherwise execute will perform the wrong action.
	parser.add_option("-d", "--down", action="callback", dest="down", callback=optional_arg_callback("0"), help="rollback table_base version DOWN")
	parser.add_option("-v", "--ver", action="store_true", dest="ver", help="report version of table_base")
	parser.add_option("-c", "--config", dest="config", help="config file")

	parser.set_defaults(up = True)
	parser.set_defaults(down = False)
	parser.set_defaults(ver = False)

	return parser
