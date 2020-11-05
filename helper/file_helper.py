# -*-coding:utf-8-*-
# The script has been tested successfully.

import os
import pickle

projects = [
    # 'kafka',  # 25 -> 23
    'flink',  # 89 ->83
    # 'zookeeper',  # 20-> 19
    # 'hadoop',  # 280 -> 214
    # 'cassandra',  # 9 -> 3
    # 'storm',  # 38 ->34
    # 'beam',  # 68 -> 56
    # 'groovy',  # 57 -> 56
    # 'hbase',  # 64 -> 57
    # 'ignite',  # 380 -> 334

    # 'camel',
    # 'hive',
    # 'shiro',
    # 'kylin',
    # 'curator',
    # 'nifi',
    # 'mvn',  # maven
    # 'nutch',
    # 'calcite',
    # 'flume',

]

root_path = r'D:/CLDP_data'
dataset_paths = dict(zip(projects, [f'{root_path}/Dataset/{proj}' for proj in projects]))
code_repos_paths = dict(zip(projects, [f'{root_path}/Repository/{proj}' for proj in projects]))
analysis_file_paths = dict(zip(projects, [f'{root_path}/Analysis/{proj}' for proj in projects]))
version_file_paths = dict(zip(projects, [f'{root_path}/Version/{proj}.csv' for proj in projects]))


def make_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_data_to_file(path, data):
    with open(path, 'w', encoding='utf-8') as fw:
        fw.write(data)


def read_data_from_file(path):
    with open(path, 'r', encoding='utf-8', errors="ignore") as fr:
        lines = fr.readlines()
    return lines


def dump_pk_result(path, data):
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def load_pk_result(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data


def is_test_file(src_file):
    return 'test/' in src_file or 'tests/' in src_file or src_file.endswith('Test.java')


def is_comment_line(target_line):
    return target_line.endswith(')') or target_line.startswith('//') or target_line.startswith('/*') \
           or target_line.startswith('*') or target_line.endswith('*/')
