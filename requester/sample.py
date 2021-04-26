import boto3
import pprint
import time
import uuid

_timestamp = int(time.time())
print(_timestamp)

ec2 = boto3.client('ec2')
responce = ec2.describe_instances()

pseudo_table_dict = {}

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

def _f(_arg_instance_dict, _arg_table, _arg_index, _arg_id, _arg_timestamp, _arg_join_key):
    for _k in list(get_dict_hierarchy(_arg_instance_dict, '', '_')):
        if isinstance(dig_dict(_arg_instance_dict, _k, '_'), list):
            _join_key = str(uuid.uuid4())
            for _i_sub, _d_sub in enumerate(dig_dict(_arg_instance_dict, _k, '_')):
                # print("_table %s" % (_arg_table.lower()))
                # print("_id: %s" % (_arg_id))
                # print("_timestamp: %s" % (_arg_timestamp))
                # print("key: %s" % (_k.lower()))
                # print("value: %s" % (_join_key))
                # if _arg_index is not None:
                #     print("_index: %s" % (_arg_index))
                # if _arg_join_key is not None:
                #     print("_join_key: %s" %(_arg_join_key))
                tmp_pseudo_table_dict = {(_arg_table.lower(), _arg_index): {_k.lower(): _join_key}}
                print("tmp_pseudo_table_dict: %s" % (tmp_pseudo_table_dict))
                # pseudo_table_dict[(_arg_table.lower(), _arg_index)] = {_k.lower(): _join_key}
                # if pseudo_table_dict[(_arg_table.lower(), _arg_index)]:
                #     tmp = pseudo_table_dict[(_arg_table.lower(), _arg_index)]
                #     tmp[_k.lower()] = _join_key
                #     pseudo_table_dict[(_arg_table.lower(), _arg_index)] = tmp
                # else:
                #     pseudo_table_dict[(_arg_table.lower(), _arg_index)] = {}

                try:
                    pseudo_table_dict[(_arg_table.lower(), _arg_index)]
                except KeyError:
                    pseudo_table_dict[(_arg_table.lower(), _arg_index)] = {}

                tmp = pseudo_table_dict[(_arg_table.lower(), _arg_index)]
                tmp[_k.lower()] = _join_key
                pseudo_table_dict[(_arg_table.lower(), _arg_index)] = tmp
                # print()
                _f(_d_sub, _arg_table + "_" + _k, _i_sub, _arg_id, _arg_timestamp, _join_key)
        else:
            flat_dict[_k] = dig_dict(_arg_instance_dict, _k, '_')
            # print("table: %s" % (_arg_table.lower()))
            # print("_id: %s" % (_arg_id))
            # print("_timestamp: %s" % (_arg_timestamp))
            # print("key: %s" % (_k.lower()))
            # print("value: %s" % (dig_dict(_arg_instance_dict, _k, '_')))
            # if _arg_index is not None:
            #     print("_index: %s" % (_arg_index))
            # if _arg_join_key is not None:
            #     print("_join_key: %s" %(_arg_join_key))
            tmp_pseudo_table_dict = {(_arg_table.lower(), _arg_index): {_k.lower(): (dig_dict(_arg_instance_dict, _k, '_'))}}
            print("tmp_pseudo_table_dict: %s" % (tmp_pseudo_table_dict))
            # pseudo_table_dict[(_arg_table.lower(), _arg_index)] = {_k.lower(): (dig_dict(_arg_instance_dict, _k, '_'))}
            # if pseudo_table_dict[(_arg_table.lower(), _arg_index)]:
            #     tmp = pseudo_table_dict[(_arg_table.lower(), _arg_index)]
            #     tmp[_k.lower()] = (dig_dict(_arg_instance_dict, _k, '_'))
            #     pseudo_table_dict[(_arg_table.lower(), _arg_index)] = tmp
            # else:
            #     pseudo_table_dict[(_arg_table.lower(), _arg_index)] = {}

            try:
                pseudo_table_dict[(_arg_table.lower(), _arg_index)]
            except KeyError:
                pseudo_table_dict[(_arg_table.lower(), _arg_index)] = {}

            tmp = pseudo_table_dict[(_arg_table.lower(), _arg_index)]
            tmp[_k.lower()] = (dig_dict(_arg_instance_dict, _k, '_'))
            tmp["_id"] = _arg_id
            tmp["_timestamp"] = _arg_timestamp
            tmp["_index"] = _arg_index
            tmp["_join_key"] = _arg_join_key
            pseudo_table_dict[(_arg_table.lower(), _arg_index)] = tmp
            # print()

for reservation in responce['Reservations']:
    for instance in reservation['Instances']:

        flat_dict = {}

        for _k_1 in list(get_dict_hierarchy(instance, '', '_')):
            if isinstance(dig_dict(instance, _k_1, '_'), list):
                for i in dig_dict(instance, _k_1, '_'):
                    for _k_2 in list(get_dict_hierarchy(i, '', '_')):
                        if isinstance(dig_dict(i, _k_2, '_'), list):
                            pass
                        else:
                            flat_dict[_k_1 + _k_2] = dig_dict(i, _k_2, '_')
            else:
                flat_dict[_k_1] = dig_dict(instance, _k_1, '_')

        pprint.pprint(flat_dict)

        _id = instance["InstanceId"]
        _f(instance, "describe_instances", None, _id, _timestamp, None)
        pprint.pprint(pseudo_table_dict)

