# -*- coding: utf-8 -*-
import boto3
import pprint
import time
import uuid

from util import DB
from util import dump
from util import show_message

_timestamp = int(time.time())

pseudo_table_dict = {}

db = DB()

def preliminary_task():
    # apis_list = [("********************", "****************************************", "ap-northeast-1", "ec2")]
    apis_list = [("737936301346", "ap-northeast-1", "ec2")]
    apis_list.append(("737936301346", "ap-northeast-1", "rds"))
    show_message("apis_list=%s" % (apis_list))
    return apis_list

def call_endpoint(_arg_apis_list):
    d = {}
    # e.g. _arg_apis_list=[("737936301346", "ap-northeast-1", "ec2")]
    # e.g. _i_api=("737936301346", "ap-northeast-1", "ec2")
    # e.g. _index=0
    for _index, _i_api in enumerate(_arg_apis_list):
        # client = boto3.client(_i_api[3], aws_access_key_id=_i_api[0], aws_secret_access_key=_i_api[1], region_name=_i_api[2])
        client = boto3.client(_i_api[2], region_name=_i_api[1])

        if _i_api[2] == "ec2":
            responce = client.describe_instances()
            # Need consideration of pagination, _index of following implementation do nothing.
        elif _i_api[2] == "rds":
            responce = client.describe_db_instances()

        new_key = _i_api + (_index, )
        d[new_key] = responce
    show_message("d=%s" % (d))
    return d

def extract_instances(_arg_responce):
    instances_dict = {}
    for _k_meta, _v_reservations in _arg_responce.items():
        instance_list = []

        if _k_meta[2] == "ec2":
            for reservation in _v_reservations['Reservations']:
                for instance in reservation['Instances']:
                    instance_list.append(instance)
        elif _k_meta[2] == "rds":
            for instance in _v_reservations['DBInstances']:
                instance_list.append(instance)

        instances_dict[_k_meta] = instance_list

    show_message("instances_dict=%s" % (instances_dict))
    return instances_dict

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

def set_value_to_pseudo_table_dict(_arg_meta_key, _arg_table_name, _arg_index, _arg_column_name, _arg_column_value, _arg_id, _arg_timestamp, _arg_join_key, _arg_instance_count):
    try:
        pseudo_table_dict[_arg_meta_key + (_arg_table_name, _arg_index, _arg_instance_count)]
    except KeyError:
        pseudo_table_dict[_arg_meta_key + (_arg_table_name, _arg_index, _arg_instance_count)] = {}

    tmp = pseudo_table_dict[_arg_meta_key + (_arg_table_name, _arg_index, _arg_instance_count)]
    tmp[_arg_column_name] = _arg_column_value
    tmp["_id"] = _arg_id
    tmp["_timestamp"] = _arg_timestamp
    tmp["_index"] = _arg_index
    tmp["_join_key"] = _arg_join_key
    pseudo_table_dict[_arg_meta_key + (_arg_table_name, _arg_index, _arg_instance_count)] = tmp

def flatten_core(_arg_instance_dict, _arg_table_name, _arg_id, _arg_timestamp, _arg_index, _arg_join_key, _arg_meta_key, _arg_instance_count):
    for _i_column_name in list(get_dict_hierarchy(_arg_instance_dict, '', '_')):
        # "Placement":{"AvailabilityZone":"ap-northeast-1c"}
        # sets _i_column_name="Placement_AvailabilityZone" and column_value="ap-northeast-1c"
        # "NetworkInterfaces":[{"Description":"Primary network interface"}]
        # sets _i_column_name="NetworkInterfaces" and column_value is a list.
        column_value = dig_dict(_arg_instance_dict, _i_column_name, '_')
        column_name = _i_column_name.lower()
        table_name = _arg_table_name.lower()

        if isinstance(column_value, list):
            _join_key = str(uuid.uuid4())
            # "SecurityGroups":[{"GroupName":"sk8393-sg-172.31.0.0.16-step"},{"GroupName":"sk8393-sg-172.31.0.0.16-webhook-github"}]
            # will be broken down as below:
            # {"GroupName":"sk8393-sg-172.31.0.0.16-step"}           - _index_of_array=0
            # {"GroupName":"sk8393-sg-172.31.0.0.16-webhook-github"} - _index_of_array=1
            for _index_of_array, _i_instance_partial_dict in enumerate(column_value):
                set_value_to_pseudo_table_dict(_arg_meta_key, table_name, _arg_index, column_name, _join_key, _arg_id, _arg_timestamp, _arg_join_key, _arg_instance_count)

                flatten_core(_i_instance_partial_dict, _arg_table_name + "_" + _i_column_name, _arg_id, _arg_timestamp, _index_of_array, _join_key, _arg_meta_key, _arg_instance_count)
        else:
            set_value_to_pseudo_table_dict(_arg_meta_key, table_name, _arg_index, column_name, column_value, _arg_id, _arg_timestamp, _arg_join_key, _arg_instance_count)

def flatten(_arg_instances):
    for _k_meta, _v_instance_list in _arg_instances.items():
        account_id = _k_meta[0]
        region = _k_meta[1]
        service = _k_meta[2]
        # key value pair of "_arg_instances" is created per json response from API endpoint.
        # If there were 100+/1000+ instances and pagination happens, is has to be stored with different key in "_arg_instances".
        dummy_index = _k_meta[3]
        for _index_instance_count, _i_instance in enumerate(_v_instance_list):
            if _k_meta[2] == "ec2":
                _id = _i_instance["InstanceId"]
                table_name = "describe_instances"
            elif _k_meta[2] == "rds":
                _id = _i_instance["DBInstanceIdentifier"]
                table_name = "describe_db_instances"

            _index = None
            _join_key = None
            flatten_core(
                _i_instance,
                table_name,
                _id,
                _timestamp,
                _index,
                _join_key,
                _k_meta,
                _index_instance_count)
    return {}

def insert():
    for _k, _v in pseudo_table_dict.items():
        table_name = _k[4]
        tmp_column_name_list = list(_v.keys())
        column_name_list = map(avoid_key_name, tmp_column_name_list)

        # tmp_create_statement_list = list(map(lambda x : x + " VARCHAR(" + VARCHAR_LENGTH + ")", column_name_list))
        tmp_create_statement_list = list(map(lambda x : x + " TEXT", column_name_list))

        create_table = "CREATE TABLE IF NOT EXISTS {0}.{1}({2}, PRIMARY KEY(_id, _timestamp, _index, _join_key));".format(
            'root',
            table_name,
            ','.join(tmp_create_statement_list)
        )

        db.create(create_table)
        db.connection.commit()


        column_name_list = list()
        value_list = list()

        id = None
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

        tmp_insert_table = "INSERT INTO {0}.{1} ({2}) VALUES(%s".format(
            'root',
            table_name,
            ','.join(list(map(lambda x : x.lower(), column_name_list)))
        )

        count = 1
        for _x in range(1, len(column_name_list)):
            tmp_insert_table += ', %s'
            count += 1
        insert_table = tmp_insert_table + ');'

        db.insert(insert_table, value_list)
        db.connection.commit()

def main():
    apis_list = preliminary_task()

    dump("apis_list.json", apis_list)

    responce = call_endpoint(apis_list)

    dump("responce.json", responce)

    instances = extract_instances(responce)

    dump("instances.json", instances)

    flatten(instances)

    dump("pseudo_table_dict.json", pseudo_table_dict)

    insert()

if __name__ == "__main__":
    main()