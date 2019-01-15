# _database.py
----
Provides a Object oriented interface for working with sqlite3 databases.

pythonjit uses a database to keep track of when source code changes, so that it knows when to recompile the static libraries.

This is a stripped down copy of pride.components.database. There are features present that are not used in pythonjit.

This module is a utility used by the library, and is not intended to be used in any other capacity.
