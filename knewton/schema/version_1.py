# vim:foldmethod=indent
from schema_base import *

class SchemaVersion1(SchemaBase):
	def __init__(self, conn):
		self.conn = conn
		self.curs = conn.cursor()
		self.ver = 1

	def up(self):
		if not self.version_exists():
			self.create_schema_versions()
			self.insert_version()
			self.close_curs()
			self.report_success(True)

	def down(self, ver):
		if self.version_exists() and self.ver >= int(ver):
			self.drop_schema_versions()
			self.report_success(False)

	def create_schema_versions(self):
		sql =  "CREATE TABLE schema_versions ("
		sql += "  id INT NOT NULL AUTO_INCREMENT,"
		sql += "  version INT NOT NULL,"
		sql += "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
		sql += "  PRIMARY KEY (id)"
		sql += ") ENGINE=InnoDB"
		self.curs.execute(sql)

	def drop_schema_versions(self):
		sql = "DROP TABLE schema_versions "
		self.curs.execute(sql)

class SchemaScriptVersions(TableBase):
	def __init__(self, conn):
		TableBase.__init__(self, conn, "schema_script_versions")
		CreateSchemaScriptVersions(self, 1)

class CreateSchemaScriptVersions(TableUpdate):
	def run_up(self):
		if not self.table_exists():
			sql =  "CREATE TABLE schema_script_versions ("
			sql += "  id INT NOT NULL AUTO_INCREMENT,"
			sql += "  version INT NOT NULL,"
			sql += "  script_name VARCHAR(255) NOT NULL,"
			sql += "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
			sql += "  PRIMARY KEY (id)"
			sql += ") ENGINE=InnoDB"
			self.curs.execute(sql)
	
	def run_down(self):
		self.drop_table()

class SchemaTableVersions(TableBase):
	def __init__(self, conn):
		TableBase.__init__(self, conn, "schema_table_versions")
		CreateSchemaTableVersions(self, 1)

class CreateSchemaTableVersions(TableUpdate):
	def run_up(self):
		if not self.table_exists():
			sql =  "CREATE TABLE schema_table_versions ("
			sql += "  id INT NOT NULL AUTO_INCREMENT,"
			sql += "  version INT NOT NULL,"
			sql += "  table_name VARCHAR(255) NOT NULL,"
			sql += "  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,"
			sql += "  PRIMARY KEY (id)"
			sql += ") ENGINE=InnoDB"
			self.curs.execute(sql)
	
	def run_down(self):
		self.drop_table()
	
	def version_exists(self):
		try:
			return TableUpdate.version_exists(self)
		except:
			return False
