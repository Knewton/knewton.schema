#!/usr/bin/python
# vim:foldmethod=indent
from knewton.schema.version_1 import SchemaVersion1, SchemaTableVersions, SchemaScriptVersions
from knewton.schema.manage import *

def up(conn, options):
	SchemaTableVersions(conn).up()
	SchemaScriptVersions(conn).up()
	exec_up(options, "tables")
	exec_up(options, "views")
	if not options.schema:
		exec_up(options, "scripts")

def main():
	(options, args) = get_local_options()
	conn = run_setup(options, 'databases/sessions.yml')
	try:
		if options.ver:
			report(conn)
		else:
			up(conn, options)
	finally:
		conn.close()
 
def get_local_options():
	parser = optionParser()
	parser.add_option("-s", "--schema", action="store_true", dest="schema", help="schema only (no scripts)")
	parser.set_defaults(schema = False)
	return parser.parse_args()

if __name__ == "__main__":
	main()
