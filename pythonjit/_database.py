""" Provides a Object oriented interface for working with sqlite3 databases.

pythonjit uses a database to keep track of when source code changes, so that it knows when to recompile the static libraries.

This is a stripped down copy of pride.components.database. There are features present that are not used in pythonjit.

This module is a utility used by the library, and is not intended to be used in any other capacity."""
import sqlite3
import contextlib
import os
import atexit

class ArgumentError(Exception):
    """ Raised when a necessary argument was not supplied to a method call. """

def create_assignment_string(items):
    """ Helper function used by Database objects """
    keys = items.keys()
    values = [items[key] for key in keys]
    return ", ".join("{} = ?".format(key) for key in keys), values

def create_where_string(where):
    """ Helper function used by Database objects """
    keys = []
    values = []
    for key, value in where.items():
        try:
            key, operator = key.split()
        except:
            operator = '='
        keys.append((key, operator))
        values.append(value)
    condition_string = "WHERE " + "AND ".join("{} {} ?".format(key, operator) for
                                              key, operator in keys)
    return condition_string, values

class Database(object):
    """ An object with methods for dispatching sqlite3 commands.
        Database objects may be simpler and safer then directly working with sqlite3 queries.
        Note that database methods commit automatically when the auto_commit attribute is set to True (defaults to True)."""
    IntegrityError = sqlite3.IntegrityError

    defaults = {"database_name" : '', "connection" : None,
                "cursor" : None, "text_factory" : str, "auto_commit" : True,
                "return_cursor" : False}

    database_structure = {}
    primary_key = {}

    def __init__(self, **kwargs):
        super(Database, self).__init__()
        kwargs.update(self.defaults)
        for attribute, value in kwargs.items():
            setattr(self, attribute, value)

        if not self.database_name:
            directory = os.path.split(__file__)[0]
            db_file = os.path.join(directory, "cache.db")
            self.database_name = os.path.join(db_file)
        self.connection, self.cursor = self.open_database(self.database_name,
                                                          self.text_factory)
        atexit.register(self.delete)

        for table, structure in self.database_structure.items():
            self.create_table(table, structure)

    def open_database(self, database_name, text_factory=None):
        """ Opens database_name and obtain a sqlite3 connection and cursor.
            Database objects call this implicitly when initializing.
            Database objects wrap the connection and store the cursor
            as Database.cursor. """
        connection = sqlite3.connect(database_name)
        if text_factory:
            connection.text_factory = text_factory
        return connection, connection.cursor()

    def create_table(self, table_name, fields, if_not_exists=True):
        """ Creates a table in the underlying sqlite3 database.
            fields is an iterable containing field names. The if_not_exists
            flag, which defaults to True, will only create the table
            if it does not exist already. """
        query = "CREATE TABLE{}{}({})".format(" IF NOT EXISTS " if
                                              if_not_exists else ' ',
                                              table_name, ', '.join(fields))
        result = self.cursor.execute(query)

        if self.auto_commit:
            self.connection.commit()
        if table_name not in self.database_structure:
            self.database_structure[table_name] = fields
            for field in fields:
                if "PRIMARY_KEY" in field.upper():
                    self.primary_key[table_name] = field.split()[0]
                    break
        return result

    def query(self, table_name, retrieve_fields=tuple(), where=None,
              group_by=None, having=None, order_by=None, distinct=True):
        """ Retrieves information from the named database table.
            retrieve_fileds is an iterable containing string names of
            the fields that should be returned. The where argument
            is a dictionary of field name:value pairs. """
        try:
            primary_key = self.primary_key[table_name]
        except KeyError:
            primary_key = ''

        retrieve_fields = ", ".join(retrieve_fields or (field.split()[0] for
                                    field in self.database_structure.get(table_name, [])))
        post_string = ''
        if group_by:
            post_string += " GROUP BY {}".format(", ".join(group_by))

        if having:
            post_string += " HAVING {}".format(having)

        if order_by:
            field_order, asc_or_desc = order_by
            post_string += " ORDER BY {} {};".format(", ".join(field_order), asc_or_desc)

        if distinct:
            pre_string = "SELECT DISTINCT {} FROM {}"
        else:
            pre_string = "SELECT {} FROM  {}"

        if where:
            condition_string, values = create_where_string(where)
            query_format = (retrieve_fields, table_name, condition_string)
            query = (pre_string + " {}").format(*query_format) + post_string
            result = self.cursor.execute(query, values)
        else:
            query = pre_string.format(retrieve_fields, table_name) + post_string
            result = self.cursor.execute(query)

        if self.return_cursor:
            return result
        else:
            result = result.fetchall()
            if result and len(result) == 1:
                result = result[0]
                if len(result) == 1:
                    result = result[0]
            return result

    def insert_into(self, table_name, values, columns=None, batch=False):
        """ Inserts values into the specified table. The values must
            be the correct type and the correct amount. Value types
            and quantity can be introspected via the table_info method."""
        # range is len(values[0]) if batch is True, else range is len(values)
        query = "INSERT INTO {}{} VALUES({})".format(table_name, columns or '',
                                                     ", ".join('?' for count in range(len(values[0 if batch else slice(len(values))]))))
        if batch:
            cursor = self.cursor.executemany(query, values)
        else:
            cursor = self.cursor.execute(query, values)
        #primary_key = values[[value for value in values if "primary_key" in value.lower()][0].split()[0]
        #self.in_memory[table_name][primary_key] = values
        if self.auto_commit:
            self.connection.commit()
        return cursor

    def update_table(self, table_name, where=None, arguments=None):
        assert where and arguments
        condition_string, values = create_where_string(where)

        _arguments = {}
        primary_key = None
        for item in self.database_structure[table_name]:
            attribute_name = item.split()[0]
            try:
                _arguments[attribute_name] = arguments[attribute_name]
            except KeyError:
                pass
            if "primary_key" in item.lower():
                primary_key = attribute_name
        #arguments = [(item, arguments[item]) for item in self.database_structure[table_name]]
        assignment_string, _values = create_assignment_string(_arguments)
        query = "UPDATE {} SET {} {}".format(table_name, assignment_string, condition_string)
        values = _values + values
        cursor = self.cursor.execute(query, values)
        if self.auto_commit:
            self.connection.commit()
        return cursor

    def delete_from(self, table_name, where=None):
        """ Removes an entry from the specified table. The where
            argument is a dictionary containing field name:value pairs."""
        if not where:
            raise ArgumentError("Failed to specify where condition(s) for {}.delete_from".format(self))
        else:
            condition_string, values = create_where_string(where)
            query = "DELETE FROM {} {}".format(table_name, condition_string)
            cursor = self.cursor.execute(query, values)
            if self.auto_commit:
                self.connection.commit()
            return cursor

    def insert_or_replace(self, table_name, new_values):
        query = "INSERT OR REPLACE INTO {} VALUES ({})".format(table_name, ', '.join('?' for value in new_values))
        cursor = self.cursor.execute(query, new_values)
        if self.auto_commit:
            self.connection.commit()
        return cursor

    def drop_table(self, table_name):
        """ Removes a table from the underlying sqlite3 database. Note
            that this will remove all entries in the specified table, and
            the data cannot be recovered."""
        self.cursor.execute("DROP TABLE {}", (table_name, ))
        if self.auto_commit:
            self.connection.commit()

    def alter_table(self, table_name, mode, argument):
        """ Alters the specified table. Available modes are
            "ADD" and "RENAME", while argument should be
            an additional field definition or new name. Added
            columns are appended. """
        if mode == "ADD":
            insert = "ADD COLUMN"
        elif mode == "RENAME":
            insert = "RENAME TO"
        else:
            raise ValueError("alter_table mode '{}' not supported".format(mode))
        command = "ALTER TABLE {} {} {}".format(table_name, insert, argument)
        self.cursor.execute(command)
        if self.auto_commit:
            self.connection.commit()

    def table_info(self, table_name):
        """ Returns a generator which yields field information for the
            specified table. Entries consist of the field index, field name,
            field type, and more."""
        return self.cursor.execute("PRAGMA table_info({})".format(table_name))

    def get_last_auto_increment_value(self, table_name):
        value = self.cursor.execute("SELECT seq FROM sqlite_sequence where name='{}'".format(table_name)).fetchone()
        if value:
            return value[0]

    def __contains__(self, table_name):
        try:
            return self.query(table_name)
        except sqlite3.OperationalError:
            return False

    def delete(self):
        self.connection.close()
        if self.delete in atexit._exithandlers:
            atexit._exithandlers.remove(self.delete)


class Cache_Database(Database):
    """ Database with the table structure expected by Import_Hook. """

    database_structure = {"Source_Cache" : ("module_name TEXT PRIMARY_KEY UNIQUE", "source_digest BLOB")}
    primary_key = {"Source_Cache" : "module_name"}


def test_db():
    """ Unit test for Database objects """
    class Test_Database(Database):

        database_structure = {"Test" : ("test_name TEXT PRIMARY_KEY UNIQUE", "test_data BLOB")}
        primary_key = {"Test" : "test_name"}

    test = Test_Database(database_name="test_database.db")

    entry = ("first_entry", "\x00" * 10)
    test.insert_into("Test", entry)
    assert test.query("Test") == entry, (entry, test.query("Test"))

    test.insert_into("Test", ("no_duplicates", "0"))
    test.insert_or_replace("Test", ("no_duplicates", '1'))
    test.query("Test", retrieve_fields=("test_name", "test_data"), where={"test_name" : "no_duplicates"})

if __name__ == "__main__":
    test_db()
