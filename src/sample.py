# -*- coding: utf-8 -*-
import boto3
import pprint
import time
import uuid

from util import DB
from util import dump
from util import show_message

pseudo_table_dict = {}

db = DB()

# terminology
# meta_key: 

def convert_to_meta_key(_arg_meta_key_in_dict_format):
    meta_key = tuple(sorted(list(_arg_meta_key_in_dict_format.items())))
    return meta_key


def convert_to_meta_key_in_dict_format(_arg_meta_key):
    meta_key_in_dict_format = dict(_arg_meta_key)
    return meta_key_in_dict_format


def preliminary_task():
    apis_list = []

    d1 = {"account_id":"737936301346", "id_attribute_name":"InstanceId", "method":"describe_instances", "region":"ap-northeast-1", "service":"ec2"}
    k1 = convert_to_meta_key(d1)
    apis_list.append(k1)

    d2 = {"account_id":"737936301346", "id_attribute_name":"DBInstanceIdentifier", "method":"describe_db_instances", "region":"ap-northeast-1", "service":"rds"}
    k2 = convert_to_meta_key(d2)
    apis_list.append(k2)

    show_message("apis_list=%s" % (apis_list))

    return apis_list


# Need consideration of pagination, _index of following implementation do nothing.
def call_endpoint(_arg_apis_list):
    api_responce = {}

    api_called_at = int(time.time())

    for _index_api_call_count, _i_meta_key in enumerate(_arg_apis_list):
        meta_key_in_dict_format = convert_to_meta_key_in_dict_format(_i_meta_key)

        account_id = meta_key_in_dict_format.get("account_id", None)
        method = meta_key_in_dict_format.get("method", None)
        region = meta_key_in_dict_format.get("region", None)
        service = meta_key_in_dict_format.get("service", None)

        client = boto3.client(service, region_name=region)

        object_method = getattr(client, method)
        responce = object_method()

        meta_key_in_dict_format["api_call_count"] = _index_api_call_count
        meta_key_in_dict_format["api_called_at"] = api_called_at
        meta_key = convert_to_meta_key(meta_key_in_dict_format)
        api_responce[meta_key] = responce

    show_message("api_responce=%s" % (api_responce))

    return api_responce


def extract_instances(_arg_responce):
    instances_dict = {}
    for _k_meta_key, _v_peel1 in _arg_responce.items():
        meta_key_in_dict_format = convert_to_meta_key_in_dict_format(_k_meta_key)

        account_id = meta_key_in_dict_format.get("account_id", None)
        api_call_count = meta_key_in_dict_format.get("api_call_count", None)
        method = meta_key_in_dict_format.get("method", None)
        region = meta_key_in_dict_format.get("region", None)
        service = meta_key_in_dict_format.get("service", None)

        instance_list = []

        if service == "ec2":
            for reservation in _v_peel1['Reservations']:
                for instance in reservation['Instances']:
                    instance_list.append(instance)
        elif service == "rds":
            for instance in _v_peel1['DBInstances']:
                instance_list.append(instance)

        instances_dict[_k_meta_key] = instance_list

    show_message("instances_dict=%s" % (instances_dict))
    return instances_dict


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


def set_value_to_pseudo_table_dict(_arg_meta_key, _arg_column_name, _arg_column_value):
    if _arg_meta_key in pseudo_table_dict:
        pass
    else:
        pseudo_table_dict[_arg_meta_key] = {}

    meta_key_in_dict_format = convert_to_meta_key_in_dict_format(_arg_meta_key)

    id = meta_key_in_dict_format.get("id", None)
    api_called_at = meta_key_in_dict_format.get("api_called_at", None)
    index_of_array = meta_key_in_dict_format.get("index_of_array", None)
    join_key = meta_key_in_dict_format.get("join_key", None)
    account_id = meta_key_in_dict_format.get("account_id", None)
    region = meta_key_in_dict_format.get("region", None)

    tmp = pseudo_table_dict[_arg_meta_key]
    tmp[_arg_column_name] = _arg_column_value
    tmp["_id"] = id
    tmp["_timestamp"] = api_called_at
    tmp["_index"] = index_of_array
    tmp["_join_key"] = join_key
    tmp["_account_id"] = account_id
    tmp["_region"] = region
    pseudo_table_dict[_arg_meta_key] = tmp


def flatten_core(_arg_instance_dict, _arg_table_name, _arg_meta_key):
    meta_key_in_dict_format = convert_to_meta_key_in_dict_format(_arg_meta_key)
    for _i_column_name in list(get_dict_hierarchy(_arg_instance_dict, '', '_')):
        # "Placement":{"AvailabilityZone":"ap-northeast-1c"}
        # sets _i_column_name="Placement_AvailabilityZone" and column_value="ap-northeast-1c"
        # "NetworkInterfaces":[{"Description":"Primary network interface"}]
        # sets _i_column_name="NetworkInterfaces" and column_value is a list.
        column_value = dig_dict(_arg_instance_dict, _i_column_name, '_')
        column_name = _i_column_name.lower()
        table_name = meta_key_in_dict_format.get("table_name", None)

        if isinstance(column_value, list):
            join_key = str(uuid.uuid4())
            meta_key_in_dict_format["join_key"] = join_key
            set_value_to_pseudo_table_dict(
                _arg_meta_key,
                column_name,
                join_key
            )

            # "SecurityGroups":[{"GroupName":"sk8393-sg-172.31.0.0.16-step"},{"GroupName":"sk8393-sg-172.31.0.0.16-webhook-github"}]
            # will be broken down as below:
            # {"GroupName":"sk8393-sg-172.31.0.0.16-step"}           - _index_of_array=0
            # {"GroupName":"sk8393-sg-172.31.0.0.16-webhook-github"} - _index_of_array=1
            for _index_of_array, _i_instance_partial_dict in enumerate(column_value):
                meta_key_in_dict_format["index_of_array"] = _index_of_array
                meta_key_in_dict_format["table_name"] = (_arg_table_name + "_" + _i_column_name).lower()
                meta_key_in_dict_format["parent_table"] = _arg_table_name.lower()
                meta_key_in_dict_format["parent_column"] = _i_column_name.lower()
                new_meta_key = convert_to_meta_key(meta_key_in_dict_format)

                flatten_core(
                    _i_instance_partial_dict,
                    _arg_table_name + "_" + _i_column_name,
                    new_meta_key
                )
        else:
            set_value_to_pseudo_table_dict(
                _arg_meta_key,
                column_name,
                column_value
            )


def flatten(_arg_instances):
    for _k_meta_key, _v_instance_list in _arg_instances.items():
        meta_key_in_dict_format = convert_to_meta_key_in_dict_format(_k_meta_key)

        id_attribute_name = meta_key_in_dict_format.get("id_attribute_name", None)
        method = meta_key_in_dict_format.get("method", None)
        service = meta_key_in_dict_format.get("service", None)

        for _index_instance_count, _i_instance in enumerate(_v_instance_list):
            meta_key_in_dict_format["id"] = _i_instance[id_attribute_name]
            table_name = "{0}_{1}".format(service.lower(), method.lower())
            meta_key_in_dict_format["table_name"] = table_name
            meta_key_in_dict_format["index_of_array"] = None
            meta_key_in_dict_format["join_key"] = None
            meta_key_in_dict_format["parent_table"] = None
            meta_key_in_dict_format["parent_column"] = None
            meta_key = convert_to_meta_key(meta_key_in_dict_format)

            flatten_core(
                _i_instance,
                table_name,
                meta_key)

    return {}


def insert():
    for _k_meta_key, _v in pseudo_table_dict.items():
        meta_key_in_dict_format = convert_to_meta_key_in_dict_format(_k_meta_key)
        table_name = meta_key_in_dict_format.get("table_name", None)

        column_name_list = list()
        value_list = list()
        id = None
        for k, v in sorted(_v.items(), key=lambda x:x[0]):
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

        tmp_create_statement_list = list(map(lambda x : x + " TEXT", column_name_list))

        create_table = "CREATE TABLE IF NOT EXISTS {0}.{1}({2}, PRIMARY KEY(_account_id, _id, _index, _join_key, _region, _timestamp));".format(
            'root',
            table_name,
            ','.join(tmp_create_statement_list)
        )

        db.create(create_table)
        db.connection.commit()

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