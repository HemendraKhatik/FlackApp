"""
@author:    kaloneh <kaloneh@gmail.com>
@comment:   Data Management Language (DML) on user table with respect to associated file (e.g., user_channel_table.sql as default)
"""
import re


class AbstractSchema:
    def __init__(self, db, table, **kwargs):
        associated_sql = kwargs.get('associated_sql', "{tbl}_table.sql".format(tbl=table))
        sql_delimiter = kwargs.get('sql_delimiter', ";")

        def _queries():
            _queries = {"create_table": None, "create_sequence": [], "alter_table": [], "drop_table": None}
            pos = lambda r, q: re.compile(r, re.IGNORECASE).fullmatch(q)
            with open(associated_sql, 'r') as qs:
                queries = "".join(filter(lambda l: l.strip() != '', list(
                    map(
                        lambda line: line.strip() if not line.strip().startswith("--") else "",
                        qs.readlines()
                    )))).split(sql_delimiter)
                for q in queries:
                    if pos("^\s*create\s+table\s+.+", q) is not None:
                        _queries['create_table'] = q.strip()
                    elif pos("^\s*create\s+sequence\s+.+", q) is not None:
                        _queries['create_sequence'].append(q.strip())
                    elif pos("^\s*alter\s+table\s+.+", q) is not None:
                        _queries['alter_table'].append(q.strip())
                    elif pos("^\s*drop\s+table\s+.+", q) is not None:
                        _queries['drop_table'] = q.strip()
            return _queries

        self._db = db
        self._queries = _queries()

    def queries(self):
        return self._queries

    def execute(self, build, schema=None):
        """
        create or drop user_table from either direct sql query schema or user_channel_table.sql
        :param build: bool: it creates table and all indexes if the build parameter will set to :True unless drops table
        :param schema: either of valid sql query and :None
        :return: execution query result will be returned if schema is a valid sql query and user has privilege
        unless raises an :Exception
        """
        try:
            if schema == None:
                schema = self._queries['drop_table'];
                if build:
                    q, s, a = (self._queries['create_table'], ";\n".join(self._queries['create_sequence']),
                               ";\n".join(self._queries['alter_table']))
                    schema = ";\n".join([q, s, a])
            print(schema)
            table = self._db.execute(":schema", {"schema": schema})
            return table
        except Exception as e:
            raise "%s" % e


__all__ = ['AbstractSchema', 'schemas']
