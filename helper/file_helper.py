# -*-coding:utf-8-*-
# The script has been tested successfully.

import os
import pickle

projects = [
    # 'kafka', 'flink', 'hadoop', 'zookeeper',
    'cassandra',  # 'storm', 'beam', 'groovy', 'hbase', 'ignite',
]

'''
'camel',
'hive',
'shiro',
'kylin',
'curator',
'nifi',
'mvn',  # maven
'nutch',
'calcite',
'flume',
'''

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
