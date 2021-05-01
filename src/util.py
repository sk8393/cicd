import io
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

def show_message(msg, newline=True, show_timestamp=True, _arg_function='', _arg_function_enter=0, _arg_function_exit=0, _arg_callback_id=''):
    try:
        sys.stdout.write(
            "%s%s%s%s" % (
                ("%s : " % datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if show_timestamp else "",
                "[%s]" % HOSTNAME[:4],
                msg,
                "\n" if newline else ""))
        sys.stdout.flush()

        body_dict = dict()
        body_dict['callback_id'] = _arg_callback_id
        body_dict['function'] = _arg_function
        body_dict['function_enter'] = _arg_function_enter
        body_dict['function_exit'] = _arg_function_exit
        body_dict['hostname'] = HOSTNAME
        body_dict['message'] = str(msg)
        now = datetime.now()
        body_dict['@timestamp'] = now.strftime("%Y-%m-%dT%H:%M:%S.") + "%03d" % (now.microsecond // 1000)

        sender.setup(
                'awssql.logs',
                host = 'localhost',
                port=8888)
        event.Event(
                'follow',
                body_dict)
    except UnicodeEncodeError:
        show_message(type(e))
        show_message(e.args)
        traceback.print_exc()


class DB:
    def __init__(self, _arg_user=DB_ROOT_USER, _arg_password=DB_ROOT_PASSWORD):
        retry_count = 1
        while retry_count <= int(DB_CONNECTION_RETRY):
            try:
                self.connection = psycopg2.connect(
                        "host={0} port={1} user={2} password={3} dbname={4}"
                        .format(DB_HOST, DB_PORT, _arg_user, _arg_password, DB_NAME))
                break
            except psycopg2.OperationalError as e:
                exception_message_list = list()
                for _x in e.args:
                    exception_message_list.append(str(_x))
                exception_messages = ','.join(exception_message_list)
                postgres_cannot_connect_server = re.search(r"could not connect to server", exception_messages)
                if postgres_cannot_connect_server:
                    show_message(type(e))
                    show_message(e.args)
                    show_message("Retry count is {0}, going to wait {1} second(s).".format(retry_count, retry_count**2))
                    time.sleep(retry_count**2)
                    retry_count += 1
                else:
                    traceback.print_exc()
                    exit()

        self.cursor = self.connection.cursor()


    def __del__(self):
        self.cursor.close()
        self.connection.close()


    def create(self, _arg_sql_create_statement):
        try:
            self.cursor.execute(_arg_sql_create_statement)
            self.connection.commit()
        except psycopg2.ProgrammingError as e:
            exception_message_list = list()
            for _x in e.args:
                exception_message_list.append(str(_x))
            exception_messages = ','.join(exception_message_list)
            postgres_table_already_exists = re.search(r"relation .* already", exception_messages)
            postgres_schema_already_exists = re.search(r"schema .* already exists", exception_messages)
            postgres_role_already_exists = re.search(r"role .* already exists", exception_messages)
            cannot_drop_columns_from_view = re.search(r"cannot drop columns from view", exception_messages)
            if postgres_table_already_exists or postgres_schema_already_exists or postgres_role_already_exists or cannot_drop_columns_from_view:
                show_message(type(e))
                show_message(e.args)
            else:
                traceback.print_exc()
                exit()


    # Expect that value passed as list.
    def insert(self, _arg_sql_insert_statement, _arg_insert_value_list):
        try:
            self.cursor.execute(
                    _arg_sql_insert_statement,
                    _arg_insert_value_list)
        except psycopg2.IntegrityError as e:
            exception_message_list = list()
            for _x in e.args:
                exception_message_list.append(str(_x))
            exception_messages = ','.join(exception_message_list)
            postgres_duplicate_entry = re.search(r"duplicate key value violates unique constraint .*", exception_messages)
            if postgres_duplicate_entry:
                show_message(type(e))
                show_message(e.args)
            else:
                traceback.print_exc()
                exit()
        except psycopg2.errors.UndefinedColumn as e:
            exception_message_list = list()
            for _x in e.args:
                exception_message_list.append(str(_x))
            exception_messages = ','.join(exception_message_list)
            print(exception_messages)
            exit()


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