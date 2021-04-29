import boto3
import pprint
import time
import uuid

from util import DB
from util import show_message

_timestamp = int(time.time())

ec2 = boto3.client('ec2')
responce = ec2.describe_instances()

pseudo_table_dict = {}

db = DB()
VARCHAR_LENGTH = '64'

def avoid_key_name(_arg_column_name):
    if _arg_column_name.lower() == "primary":
        return "_primary"
    else:
        return _arg_column_name

def get_dict_hierarchy(target_dict, root_path, sep):
    if isinstance(target_dict, dict):
        for key in target_dict.keys():
            value = target_dict[key]
            target_path = root_path + sep + key
            if not isinstance(value, dict):
                yield target_path[1:]
            else:
                yield from get_dict_hierarchy(value, target_path, sep)

def dig_dict(target_dict, target_branch, sep):
    limbs = target_branch.split(sep)
    leaf = target_dict
    for one_limb in limbs:
        leaf = leaf[one_limb]
    return leaf

def _flatten(_arg_instance_dict, _arg_table_name, _arg_id, _arg_timestamp, _arg_index, _arg_join_key):
    for _column_name in list(get_dict_hierarchy(_arg_instance_dict, '', '_')):
        if isinstance(dig_dict(_arg_instance_dict, _column_name, '_'), list):
            _join_key = str(uuid.uuid4())
            for _index_sub, _dict_sub in enumerate(dig_dict(_arg_instance_dict, _column_name, '_')):
                tmp_pseudo_table_dict = {(_arg_table_name.lower(), _arg_index): {_column_name.lower(): _join_key}}

                try:
                    pseudo_table_dict[(_arg_table_name.lower(), _arg_index)]
                except KeyError:
                    pseudo_table_dict[(_arg_table_name.lower(), _arg_index)] = {}

                tmp = pseudo_table_dict[(_arg_table_name.lower(), _arg_index)]
                tmp[_column_name.lower()] = _join_key
                tmp["_id"] = _arg_id
                tmp["_timestamp"] = _arg_timestamp
                tmp["_index"] = _arg_index
                tmp["_join_key"] = _arg_join_key
                pseudo_table_dict[(_arg_table_name.lower(), _arg_index)] = tmp

                _flatten(_dict_sub, _arg_table_name + "_" + _column_name, _arg_id, _arg_timestamp, _index_sub, _join_key)
        else:
            tmp_pseudo_table_dict = {(_arg_table_name.lower(), _arg_index): {_column_name.lower(): (dig_dict(_arg_instance_dict, _column_name, '_'))}}

            try:
                pseudo_table_dict[(_arg_table_name.lower(), _arg_index)]
            except KeyError:
                pseudo_table_dict[(_arg_table_name.lower(), _arg_index)] = {}

            tmp = pseudo_table_dict[(_arg_table_name.lower(), _arg_index)]
            tmp[_column_name.lower()] = (dig_dict(_arg_instance_dict, _column_name, '_'))
            tmp["_id"] = _arg_id
            tmp["_timestamp"] = _arg_timestamp
            tmp["_index"] = _arg_index
            tmp["_join_key"] = _arg_join_key
            pseudo_table_dict[(_arg_table_name.lower(), _arg_index)] = tmp

for reservation in responce['Reservations']:
    for instance in reservation['Instances']:
        _id = instance["InstanceId"]
        _index = None
        _join_key = None
        _flatten(instance, "describe_instances", _id, _timestamp, _index, _join_key)

        # pprint.pprint(pseudo_table_dict)

        for _k, _v in pseudo_table_dict.items():
            table_name = _k[0]
            tmp_column_name_list = list(_v.keys())
            column_name_list = map(avoid_key_name, tmp_column_name_list)
            # print(table_name)
            # print(_v.keys())

            tmp_create_statement_list = list(map(lambda x : x + " VARCHAR(" + VARCHAR_LENGTH + ")", column_name_list))
            # print(tmp_create_statement_list)

            create_table = """
                    CREATE TABLE {0}.{1}({2}, PRIMARY KEY(_id, _timestamp, _index, _join_key));""".format(
                            'root',
                            table_name,
                            ','.join(tmp_create_statement_list))
            # print(create_table)

            db.create(create_table)
            db.connection.commit()


            column_name_list = list()
            value_list = list()

            id = None
            print(_v)
            for k, v in _v.items():
                if len(k) <= 63:
                    if k.lower()== 'primary' or k=='DEFAULT' or k=='END':
                        column_name_list.append('_' + k.lower())
                    else:
                        column_name_list.append(k.lower())
                else:
                    # Column length is up to 63, this is restriction of PostgreSQL.
                    # Inserting another if block is annoying, so just set 63 at here.
                    # So, some column name might be truncated.
                    column_name_list.append(k[-63:])
                try:
                    str(v).encode('ascii')
                    value_list.append(str(v))
                except UnicodeEncodeError as e:
                    show_message(type(e))
                    show_message(e.args)
                    value_list.append('?')

            tmp_insert_table = """
                    INSERT INTO {0}.{1} ({2}) VALUES(%s""".format(
                            'root',
                            table_name,
                            ','.join(list(map(lambda x : x.lower(), column_name_list))))
            count = 1
            for _x in range(1, len(column_name_list)):
                tmp_insert_table += ', %s'
                count += 1
            insert_table = tmp_insert_table + ');'
            print(insert_table)

            db.insert(insert_table, value_list)
            db.connection.commit()
