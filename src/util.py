import io
import inspect
import json
import os
import psycopg2
import re
import sys
import time
import traceback

from datetime import date, datetime
from fluent import sender
from fluent import event

DB_CONNECTION_RETRY = 3
DB_HOST = "postgres"
DB_NAME = os.environ['POSTGRES_DB_NAME']
DB_PORT = 5432
DB_ROOT_PASSWORD = os.environ['POSTGRES_SUPERUSER_PASSWORD']
DB_ROOT_SCHEMA = os.environ['POSTGRES_SUPERUSER_SCHEMA']
DB_ROOT_USER = os.environ['POSTGRES_SUPERUSER']
HOSTNAME = os.environ['HOSTNAME']

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def json_serial(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def dump(_arg_file_name, _arg_object):
    f = open(_arg_file_name, "w")
    if isinstance(_arg_object, dict):
        d = {}
        for _k, _v in _arg_object.items():
            if isinstance(_k, tuple):
                d[str(_k)] = _v
            else:
                d[_k] = _v
        json.dump(d, f, default=json_serial, indent=2)
    else:
        json.dump(_arg_object, f, default=json_serial, indent=2)
    f.close()


def show_message(_arg_message):
    try:
        now = datetime.now()
        hostname = HOSTNAME
        function = (inspect.stack()[1].filename[:-len(".py")] if inspect.stack()[1].filename.endswith(".py") else inspect.stack()[1].filename) + "." + inspect.stack()[1].function,
        message = str(_arg_message).strip()

        sys.stdout.write(
            "%s%s%s%s%s" % (
                ("%s: " % now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]),
                "[%s] " % hostname[:6],
                "%s: " % function,
                message,
                "\n"
            )
        )
        sys.stdout.flush()

        body_dict = dict()
        body_dict['@timestamp'] = now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03d" % (now.microsecond // 1000)
        body_dict['hostname'] = hostname
        body_dict['function'] = function
        body_dict['message'] = message

        sender.setup(
                'awssql.logs',
                host = 'localhost',
                port=8888)
        event.Event(
                'follow',
                body_dict)
    except UnicodeEncodeError:
        show_message("type(e)=%s" % (type(e)))
        show_message("e.args=%s" % (e.args))
        traceback.print_exc()


class DB:
    def __init__(self, _arg_user=DB_ROOT_USER, _arg_password=DB_ROOT_PASSWORD):
        retry_count = 1
        while retry_count <= int(DB_CONNECTION_RETRY):
            try:
                self.connection = psycopg2.connect(
                    "host={0} port={1} user={2} password={3} dbname={4}".format(
                        DB_HOST,
                        DB_PORT,
                        _arg_user,
                        _arg_password,
                        DB_NAME
                    )
                )
                break
            except psycopg2.OperationalError as e:
                exception_message_list = list()
                for _x in e.args:
                    exception_message_list.append(str(_x))
                exception_messages = ','.join(exception_message_list)
                postgres_cannot_connect_server = re.search(r"could not connect to server", exception_messages)
                if postgres_cannot_connect_server:
                    show_message("type(e)=%s" % (type(e)))
                    show_message("e.args=%s" % (e.args))
                    show_message("Retry count is {0}, going to wait {1} second(s).".format(retry_count, retry_count**2))
                    time.sleep(retry_count**2)
                    retry_count += 1
                else:
                    traceback.print_exc()
                    exit()

        self.connection.autocommit = True
        self.cursor = self.connection.cursor()


    def __del__(self):
        self.cursor.close()
        self.connection.close()


    def get_exception_messages(self, _arg_exception):
        exception_message_list = list()
        for _i_exception in _arg_exception.args:
            exception_message_list.append(str(_i_exception))
        exception_messages = ','.join(exception_message_list)
        show_message("exception_messages=%s" % (exception_messages))
        return exception_messages


    def create(self, _arg_sql_create_statement, _arg_parent_table=None, _arg_parent_column=None):
        try:
            show_message("_arg_sql_create_statement=%s" % (_arg_sql_create_statement))
            self.cursor.execute(_arg_sql_create_statement)
        except psycopg2.errors.InvalidForeignKey as e:
            exception_messages = self.get_exception_messages(e)
            no_unique_constraint = re.search(
                r"there is no unique constraint matching given keys for referenced table \"(\w*?)\"",
                exception_messages
            )
            if no_unique_constraint:
                # referenced_table = no_unique_constraint.group(1)
                self.add_unique(_arg_parent_table, _arg_parent_column)
                self.create(
                    _arg_sql_create_statement,
                    _arg_parent_table=_arg_parent_table,
                    _arg_parent_column=_arg_parent_column
                )
            else:
                traceback.print_exc()
                exit()
        except psycopg2.ProgrammingError as e:
            exception_messages = self.get_exception_messages(e)
            relation_already_exists = re.search(r"relation .* already exists", exception_messages)
            schema_already_exists = re.search(r"schema .* already exists", exception_messages)
            role_already_exists = re.search(r"role .* already exists", exception_messages)
            cannot_drop_columns_from_view = re.search(r"cannot drop columns from view", exception_messages)
            if relation_already_exists or schema_already_exists or role_already_exists or cannot_drop_columns_from_view:
                pass
            else:
                traceback.print_exc()
                exit()


    def insert(self, _arg_sql_insert_statement, _arg_insert_value_list):
        try:
            show_message("_arg_sql_insert_statement=%s" % (_arg_sql_insert_statement))
            show_message("_arg_insert_value_list=%s" % (_arg_insert_value_list))
            self.cursor.execute(_arg_sql_insert_statement, _arg_insert_value_list)
        except psycopg2.IntegrityError as e:
            exception_messages = self.get_exception_messages(e)
            duplicate_key_value_violates_unique_constraint = re.search(r"duplicate key value violates unique constraint .*", exception_messages)
            if duplicate_key_value_violates_unique_constraint:
                pass
            else:
                traceback.print_exc()
                exit()
        except psycopg2.errors.UndefinedColumn as e:
            exception_messages = self.get_exception_messages(e)
            column_does_not_exist = re.search(r"column \"(\w*?)\" of relation \"(\w*?)\" does not exist", exception_messages)
            if column_does_not_exist:
                column = column_does_not_exist.group(1)
                table = column_does_not_exist.group(2)
                self.add_column(table, column)
                self.insert(_arg_sql_insert_statement, _arg_insert_value_list)
            else:
                traceback.print_exc()
                exit()


    def enhanced_insert(self, _arg_sql_insert_statement, _arg_insert_value_list, _arg_sql_create_statement, _arg_parent_table, _arg_parent_column):
        self.create(
            _arg_sql_create_statement,
            _arg_parent_table=_arg_parent_table,
            _arg_parent_column=_arg_parent_column
        )

        self.insert(_arg_sql_insert_statement, _arg_insert_value_list)


    def add_column(self, _arg_table, _arg_column):
        sql_add_column_statement = "ALTER TABLE {0}.{1} ADD COLUMN {2} {3};".format(
            DB_ROOT_SCHEMA,
            _arg_table,
            _arg_column,
            "TEXT"
        )
        show_message("sql_add_column_statement=%s" % (sql_add_column_statement))
        self.cursor.execute(sql_add_column_statement)


    def add_unique(self, _arg_parent_table, _arg_parent_column):
        sql_add_unique_statement = "ALTER TABLE {0}.{1} ADD UNIQUE({2});".format(
            DB_ROOT_SCHEMA,
            _arg_parent_table,
            _arg_parent_column
        )
        show_message("sql_add_unique_statement=%s" % (sql_add_unique_statement))
        self.cursor.execute(sql_add_unique_statement)