#!/usr/bin/python
# vim:foldmethod=indent
from knewton.schema.base import *
from knewton.schema.run import execute

class AuthTokens(TableBase):
	def __init__(self, conn):
		TableBase.__init__(self, conn, "auth_tokens")
		CreateAuthTokens(self, 1)
		AddInsertTrigger(self, 2)
		AddUpdateTrigger(self, 3)
		AddTokenUniqueKey(self, 4)
		ModifyUserIdNullable(self, 5)
		DropTokenNonuniqueKey(self, 6)
		AlterCreatedAtDefault(self, 7)
		AlterUpdatedAtDefault(self, 8)
		RemoveUpdateTrigger(self, 9)
		RemoveInsertTrigger(self, 10)
		AddInsertTrigger(self, 11)
		DropSession(self, 12)
		ChangeEngine(self, 13)
		AddLastAuthenticationTypeColumn(self, 14)
		RevertEngine(self, 15)

class CreateAuthTokens(TableUpdate):
	def run_up(self):
		if not self.table_exists():
			sql  = "CREATE TABLE auth_tokens ("
			sql += "  id INT NOT NULL AUTO_INCREMENT,"
			sql += "  user_id INT NOT NULL,"
			sql += "  token VARCHAR(255),"
			sql += "  sequence INT,"
			sql += "  session TEXT,"
			sql += "  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
			sql += "  updated_at TIMESTAMP NOT NULL,"
			sql += "  PRIMARY KEY (id),"
			sql += "  KEY (token),"
			sql += "  KEY (user_id)"
			sql += ") ENGINE=InnoDB"
			self.curs.execute(sql)

	def run_down(self):
		self.drop_table()

class AddInsertTrigger(TableUpdate):
	def run_up(self):
		create_insert_trigger(self.curs, self.parent.name, create=True)

	def run_down(self):
		drop_insert_trigger(self.curs, self.parent.name)

class AddUpdateTrigger(TableUpdate):
	def run_up(self):
		create_update_trigger(self.curs, self.parent.name)

	def run_down(self):
		drop_update_trigger(self.curs, self.parent.name)

class AddTokenUniqueKey(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " ADD UNIQUE KEY (token)"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " DROP KEY token_2"
		self.curs.execute(sql)

class ModifyUserIdNullable(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " MODIFY COLUMN user_id INT"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " MODIFY COLUMN user_id INT NOT NULL"
		self.curs.execute(sql)

class DropTokenNonuniqueKey(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " DROP KEY token"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " ADD KEY (token)"
		self.curs.execute(sql)

class AlterCreatedAtDefault(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " MODIFY COLUMN created_at TIMESTAMP DEFAULT 0"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " MODIFY COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
		self.curs.execute(sql)

class AlterUpdatedAtDefault(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " MODIFY COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " MODIFY COLUMN updated_at TIMESTAMP DEFAULT 0"
		self.curs.execute(sql)

class RemoveUpdateTrigger(TableUpdate):
	def run_up(self):
		drop_update_trigger(self.curs, self.parent.name)

	def run_down(self):
		create_update_trigger(self.curs, self.parent.name)

class RemoveInsertTrigger(TableUpdate):
	def run_up(self):
		drop_insert_trigger(self.curs, self.parent.name)

	def run_down(self):
		create_insert_trigger(self.curs, self.parent.name)

class DropSession(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " DROP COLUMN session"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " ADD COLUMN session TEXT AFTER sequence"
		self.curs.execute(sql)

class ChangeEngine(TableUpdate):
	def run_up(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " ENGINE Memory"
		self.curs.execute(sql)

	def run_down(self):
		sql  = "ALTER TABLE %s" % self.parent.name
		sql += " ENGINE InnoDB"
		self.curs.execute(sql)

class RevertEngine(ChangeEngine):
	def run_up(self):
		ChangeEngine.run_down(self)

	def run_down(self):
		ChangeEngine.run_up(self)

class AddLastAuthenticationTypeColumn(TableUpdate):
	def run_up(self):
		sql = "ALTER TABLE %s ADD COLUMN last_authentication_type VARCHAR(20) AFTER sequence" % self.parent.name
		self.curs.execute(sql)

	def run_down(self):
		sql = "ALTER TABLE %s DROP COLUMN last_authentication_type" % self.parent.name
		self.curs.execute(sql)

if __name__ == "__main__":
	execute(AuthTokens, 'databases/sessions.yml')
