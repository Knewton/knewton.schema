# vim:foldmethod=indent
import warnings
warnings.filterwarnings('ignore', '.*the sets module is deprecated.*', DeprecationWarning, 'MySQLdb')
import os
import glob
import re
from optparse import OptionParser
from knewton.config import *
from knewton.schema.version_1 import SchemaVersion1, SchemaTableVersions
from knewton.schema.utils import db_connect

def get_files(dirname):
	if not os.path.exists(dirname):
		raise RuntimeError(dirname + " directory missing.")
	files = []
	for infile in glob.glob( os.path.join(dirname, '*.py') ):
		m = re.match('.*?/.*?([0-9]*).*\.py', infile)
		if m:
			files.append((long(m.group(1)), infile))
	files.sort(cmp=lambda x,y: cmp(x[0], y[0]))
	return files

def exec_up(options, dirname, flags=""):
	files = get_files(dirname)
	if "-d" in flags:
		files.reverse()
	exit_codes = []
	for f in files:
		fname = f[1]
		cmd = fname
		update = ""
		if options.config:
			cmd += " -c \"" + options.config + "\" "
		if flags:
			cmd += " " + flags
		exit_codes.append(os.system(cmd))
	return exit_codes

def get_options():
	parser = optionParser()
	return parser.parse_args()

def run_setup(options, default, schema=None):
	config = None
	if options.config:
		config = options.config
	yf = fetch_config(default, config)
	if schema:
		yf['database']['database'] = schema
	return db_connect(yf['database'])

def optionParser():
	usage = "usage: %prog [options]\n\nUpdates the reporting schema to the current version"
	parser = OptionParser(usage=usage)

	parser.add_option("-u", "--up", action="store_true", dest="up", help="update to the latest schema")
	parser.add_option("-v", "--ver", action="store_true", dest="ver", help="report version of schema")
	parser.add_option("-c", "--config", dest="config", help="config file")

	parser.set_defaults(ver = False)
	parser.set_defaults(up = True)

	return parser

if __name__ == "__main__":
	main()
