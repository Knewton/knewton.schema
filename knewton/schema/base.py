# vim:foldmethod=indent
class SchemaBase(object):
	def version_exists(self):
		try:
			sql = "SELECT version FROM schema_versions WHERE version = %s"
			self.curs.execute(sql, self.ver)
			result = self.curs.fetchone()
			if result is not None:
				return True
			else:
				return False
		except:
			return False

	def report_success(self, up):
		if up:
			print "Schema upgraded to version", self.ver
		else:
			print "Schema downgraded from version", self.ver

	def insert_version(self):
		sql = "INSERT INTO schema_versions" \
			+ " (version, created_at)" \
			+ " VALUES (" + str(self.ver) + ", NOW())"
		ret = self.curs.execute(sql)

	def delete_version(self):
		sql = "DELETE FROM schema_versions" \
			+ " WHERE version = " +  str(self.ver)
		ret = self.curs.execute(sql)

	def close_curs(self):
		self.conn.commit()
		self.curs.close()

	def drop_table(self, table):
		try:
			sql = "DROP TABLE %s" % table
			self.curs.execute(sql)
		except Exception, e:
			print "table drop failed: ", e

	def drop_view(self, table):
		try:
			sql = "DROP VIEW IF EXISTS %s" % table
			self.curs.execute(sql)
		except Exception, e:
			print "view drop failed: ", e

class ViewBase(object):
	def report_success(self, up):
		if up:
			print "Views upgraded to version", self.ver
		else:
			print "Views downgraded from version", self.ver

	def close_curs(self):
		self.conn.commit()
		self.curs.close()

	def drop_view(self, table):
		try:
			sql = "DROP VIEW IF EXISTS %s" % table
			self.curs.execute(sql)
		except Exception, e:
			print "view drop failed: ", e

class TableUpdate(object):
	def __init__(self, parent, version):
		self.parent = parent
		self.curs = parent.curs
		self.ver = version
		self.parent.add_update(self)

	def version_exists(self):
		sql =  "SELECT version"
		sql += " FROM schema_table_versions"
		sql += " WHERE version = %s"
		sql += "  AND table_name = %s"
		self.curs.execute(sql, [self.ver, self.parent.name])
		result = self.curs.fetchone()
		if result is not None:
			return True
		else:
			return False

	def check_prerequisite(self, table, version):
		return check_table_prerequisite(self.curs, table, version)

	def report_success(self, up):
		if up:
			print "Table", self.parent.name, "upgraded to version", self.ver
		else:
			print "Table", self.parent.name, "downgraded from version", self.ver

	def insert_version(self):
		sql =  "INSERT INTO schema_table_versions"
		sql += " (version, table_name, created_at)"
		sql += " VALUES (%s, %s, NOW())"
		ret = self.curs.execute(sql, [self.ver, self.parent.name])

	def delete_version(self):
		sql = "DELETE FROM schema_table_versions"
		sql += " WHERE version = %s"
		sql += "  AND table_name = %s"
		ret = self.curs.execute(sql, [self.ver, self.parent.name])

	def up(self):
		if self.up_prerequisite_test():
			self.run_up()
			self.insert_version()
			self.report_success(True)
		else:
			print "Table", self.parent.name, self.ver, " Cannot execute upgrade due to missing prerequisite."

	def up_prerequisite_test(self):
		return True

	def run_up(self):
		pass

	def down(self):
		if self.down_prerequisite_test():
			self.run_down()
			self.delete_version()
			self.report_success(False)
		else:
			print "Table", self.parent.name, self.ver, " Cannot execute downgrade due to missing prerequisite."

	def down_prerequisite_test(self):
		return True

	def run_down(self):
		pass

	def table_exists(self):
		try:
			sql = "SHOW CREATE TABLE %s" % self.parent.name
			self.curs.execute(sql)
			return True
		except:
			return False

	def drop_table(self):
		sql = "DROP TABLE %s" % self.parent.name
		self.curs.execute(sql)

	def index_exists(self, idx):
		sql = "SHOW CREATE TABLE %s" % self.parent.name
		self.curs.execute(sql)
		result = self.curs.fetchone()
		if result[1].find(idx) > -1:
			return True
		return False

class TableBase(object):
	def __init__(self, conn, tablename):
		self.conn = conn
		self.curs = conn.cursor()
		self.name = tablename
		self.updates = []

	def ver(self):
		maxver = 0
		for update in self.updates:
			if update.ver > maxver:
				maxver = update.ver
		return maxver

	def add_update(self, update):
		if update.ver <= self.ver():
			raise RuntimeError(self.name + " already has an update with a version number higher then " + str(update.ver))
		self.updates.append(update)

	def up(self):
		for update in self.updates:
			if not update.version_exists():
				update.up()
		self.close_curs()

	def down(self, ver):
		self.updates.reverse()
		for update in self.updates:
			if update.version_exists() and update.ver >= int(ver):
				update.down()
		self.close_curs()

	def close_curs(self):
		self.conn.commit()
		self.curs.close()

	def check_version(self):
		try:
			sql = "DESC schema_table_versions"
			ret = self.curs.execute(sql)
		except:
			return 0

		try:
			sql =  "SELECT version"
			sql += " FROM schema_table_versions"
			sql += " WHERE table_name = %s"
			self.curs.execute(sql, [self.name])
			results = self.curs.fetchall()
			return results
		except:
			return 0

class ScriptBase(object):
	def __init__(self, conn):
		self.conn = conn
		self.curs = conn.cursor()
		self.updates = []

	def name(self):
		return type(self).__name__

	def ver(self):
		maxver = 0
		for update in self.updates:
			if update.ver > maxver:
				maxver = update.ver
		return maxver

	def add_update(self, update):
		if update.ver <= self.ver():
			raise RuntimeError(self.name() + " already has an update with a version number higher then " + str(update.ver))
		self.updates.append(update)

	def up(self):
		for update in self.updates:
			if not update.version_exists():
				update.up()
		self.close_curs()

	def down(self, ver):
		self.updates.reverse()
		for update in self.updates:
			if update.version_exists() and update.ver >= int(ver):
				update.down()
		self.close_curs()

	def close_curs(self):
		self.conn.commit()
		self.curs.close()

	def check_version(self):
		try:
			sql = "DESC schema_script_versions"
			ret = self.curs.execute(sql)
		except:
			return 0

		try:
			sql =  "SELECT version"
			sql += " FROM schema_script_versions"
			sql += " WHERE script_name = %s"
			self.curs.execute(sql, [self.name])
			results = self.curs.fetchall()
			return results
		except:
			return 0

class ScriptUpdate(object):
	def __init__(self, parent, version):
		self.parent = parent
		self.curs = parent.curs
		self.ver = version
		self.parent.add_update(self)

	def version_exists(self):
		sql =  "SELECT version"
		sql += " FROM schema_script_versions"
		sql += " WHERE version = %s"
		sql += "  AND script_name = %s"
		self.curs.execute(sql, [self.ver, self.parent.name()])
		result = self.curs.fetchone()
		if result is not None:
			return True
		else:
			return False

	def check_prerequisite(self, table, version):
		return check_table_prerequisite(self.curs, table, version)

	def report_success(self, up):
		if up:
			print "Script", self.parent.name(), "upgraded to version", self.ver
		else:
			print "Script", self.parent.name(), "downgraded from version", self.ver

	def insert_version(self):
		sql =  "INSERT INTO schema_script_versions"
		sql += " (version, script_name, created_at)"
		sql += " VALUES (%s, %s, NOW())"
		ret = self.curs.execute(sql, [self.ver, self.parent.name()])

	def delete_version(self):
		sql = "DELETE FROM schema_script_versions"
		sql += " WHERE version = %s"
		sql += "  AND script_name = %s"
		ret = self.curs.execute(sql, [self.ver, self.parent.name()])

	def up(self):
		if self.up_prerequisite_test():
			self.run_up()
			self.insert_version()
			self.report_success(True)
		else:
			print "Script", self.parent.name(), self.ver, " Cannot execute upgrade due to missing prerequisite."

	def up_prerequisite_test(self):
		return True

	def run_up(self):
		pass

	def down(self):
		if self.down_prerequisite_test():
			self.run_down()
			self.delete_version()
			self.report_success(False)
		else:
			print "Script", self.parent.name(), self.ver, " Cannot execute downgrade due to missing prerequisite."

	def down_prerequisite_test(self):
		return True

	def run_down(self):
		pass

def drop_view(curs, table):
	try:
		sql = "DROP VIEW IF EXISTS %s" % table
		curs.execute(sql)
	except Exception, e:
		print "view drop failed: ", e

def trigger_name(event, table):
	return "%s_%s_trg" % (event.lower(), table.lower())

def trigger_exists(curs, event, table, trigger=None):
	if trigger is None:
		trigger = trigger_name(event, table)
	sql = "SHOW TRIGGERS WHERE `Trigger` = %s and `Event` = %s"
	curs.execute(sql, [trigger, event])
	count = len(curs.fetchall())
	return (count > 0)

def create_insert_trigger(curs, table, create=False):
	sql =  "CREATE TRIGGER insert_%s_trg" % (table)
	sql += " BEFORE INSERT ON %s" % (table)
	sql += " FOR EACH ROW"
	sql += "  BEGIN"
	if create:
		sql += "   SET NEW.created_at = NOW();"
	sql += "   SET NEW.updated_at = NOW();"
	sql += "  END"
	curs.execute(sql)

def create_pausible_insert_trigger(curs, table):
	sql = "CREATE TRIGGER insert_%s_trg" % (table,)
	sql += " BEFORE INSERT ON %s" % (table,)
	sql += " FOR EACH ROW"
	sql += "  BEGIN"
	sql += "   IF (@DISABLE_TRIGGER IS NULL) THEN"
	sql += "    SET NEW.created_at = NOW();"
	sql += "    SET NEW.updated_at = NOW();"
	sql += "   END IF;"
	sql += "  END"
	curs.execute(sql)

def drop_insert_trigger(curs, table):
	sql =  "DROP TRIGGER insert_%s_trg" % (table)
	curs.execute(sql)

def create_pausible_insert_after_trigger(curs, table, replicate=False):
	sql = "CREATE TRIGGER insert_after_%s_trg" % (table,)
	sql += " AFTER INSERT ON %s" % (table,)
	sql += " FOR EACH ROW"
	sql += "  BEGIN"
	sql += "   IF (@DISABLE_TRIGGER IS NULL) THEN"
	if replicate:
		sql += "    CALL replicate_proc('%s', NEW.id, FALSE, NULL);" % (table)
	sql += "   END IF;"
	sql += "  END"
	curs.execute(sql)

def drop_insert_after_trigger(curs, table):
	sql =  "DROP TRIGGER insert_after_%s_trg" % (table)
	curs.execute(sql)

def create_update_trigger(curs, table):
	sql =  "CREATE TRIGGER update_%s_trg" % (table)
	sql += " BEFORE UPDATE ON %s" % (table)
	sql += " FOR EACH ROW"
	sql += "  BEGIN"
	sql += "   SET NEW.updated_at = NOW();"
	sql += "  END"
	curs.execute(sql)

def create_pausible_update_trigger(curs, table, replicate=False):
	sql = "CREATE TRIGGER update_%s_trg" % (table,)
	sql += " BEFORE UPDATE ON %s" % (table,)
	sql += " FOR EACH ROW"
	sql += "  BEGIN"
	sql += "   IF (@DISABLE_TRIGGER IS NULL) THEN"
	sql += "    SET NEW.updated_at = NOW();"
	if replicate:
		sql += "    CALL replicate_proc('%s', NEW.id, FALSE, NULL);" % (table)
	sql += "   END IF;"
	sql += "  END"
	curs.execute(sql)

def drop_update_trigger(curs, table):
	sql =  "DROP TRIGGER update_%s_trg" % (table)
	curs.execute(sql)

def create_pausible_delete_trigger(curs, table, replicate=False):
	sql = "CREATE TRIGGER delete_%s_trg" % (table,)
	sql += " BEFORE DELETE ON %s" % (table,)
	sql += " FOR EACH ROW"
	sql += "  BEGIN"
	sql += "   IF (@DISABLE_TRIGGER IS NULL) THEN"
	if replicate:
		sql += "    CALL replicate_proc('%s', OLD.id, TRUE, NULL);" % (table)
	sql += "   END IF;"
	sql += "  END"
	curs.execute(sql)

def drop_delete_trigger(curs, table):
	sql =  "DROP TRIGGER delete_%s_trg" % (table)
	curs.execute(sql)

def create_replication_proc(curs):
	sql =  "CREATE PROCEDURE replicate_proc(IN p_table VARCHAR(1024), IN p_id INT, IN p_del INT, IN p_ident VARCHAR(1024))"
	sql += "BEGIN"
	sql += "  INSERT INTO external_replication_actions"
	sql += "  (table_name, table_id, delete_action, delete_identifier, action_at)"
	sql += "  VALUES"
	sql += "  (p_table, p_id, p_del, p_ident, NOW());"
	sql += "END"
	curs.execute(sql)

def drop_replication_proc(curs):
	sql =  "DROP PROCEDURE replicate_proc"
	curs.execute(sql)

def create_replicate_table_proc(curs):
	sql =  "CREATE PROCEDURE replicate_table_proc(IN p_table VARCHAR(1024))"
	sql += "BEGIN"
	sql += "  SET @dyn_sql = CONCAT('INSERT INTO external_replication_actions (table_name, table_id, action_at) SELECT ''', p_table, ''', id, updated_at FROM ', p_table);"
	sql += "  PREPARE stmt FROM @dyn_sql;"
	sql += "  EXECUTE stmt;"
	sql += "END"
	curs.execute(sql)

def drop_replicate_table_proc(curs):
	sql =  "DROP PROCEDURE replicate_table_proc"
	curs.execute(sql)

def check_table_prerequisite(curs, table, version):
	try:
		sql = "DESC schema_table_versions"
		ret = curs.execute(sql)
	except:
		return False

	try:
		sql =  "SELECT *"
		sql += " FROM schema_table_versions"
		sql += " WHERE table_name = %s"
		sql += "  AND version = %s"
		curs.execute(sql, [table, version])
		results = curs.fetchall()
		if len(results) > 0:
			return True
	except:
		return False
	return False
