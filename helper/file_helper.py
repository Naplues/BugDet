# -*-coding:utf-8-*-
# The script has been tested successfully.

import os
import pickle

projects = [
    # 'ambari', # ok
    # 'amq', # ok activemq
    # 'bookkeeper',
    # 'calcite', # ok
    # 'camel', # ok
    # 'cassandra', # ok
    # 'flink',
    # 'groovy', # ok
    # 'hbase',
    # 'hive', # ok
    # 'ignite', # ok
    # 'log4j2', # logging-log4j2
    # 'mahout', # ok
    # 'mng',  # maven
    # 'nifi',
    # 'nutch',
    'storm',
    # 'tika',
    # 'ww', # struts
    # 'zookeeper', # ok
]

root_path = r'D:/CLDP_data'
dataset_paths = dict(zip(projects, [f'{root_path}/Data/{proj}' for proj in projects]))
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


def is_comment_line2(target_line):
    line = target_line.strip()
    return line.endswith(')') or line.startswith('//') or line.startswith('/*') or line.startswith(
        '*') or line.endswith('*/') or line == '' or line.startswith('{') or line.startswith('}')


def export_all_files_in_project(path):
    file_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = (root.replace('\\', '/') + '/' + file).replace(path, '')
            if not file_path.endswith('.java') or is_test_file(file_path):
                continue
            file_list.append(file_path)
    return file_list


if __name__ == '__main__':
    export_all_files_in_project(f'{root_path}/Repository/camel/')
