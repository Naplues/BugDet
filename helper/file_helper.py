# -*-coding:utf-8-*-
# The script has been tested successfully.
"""
The script contains the functions for file operations.
"""
import os
import pickle

from helper.config import root_path


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


def save_dict_to_file(path, data: dict):
    text = [f'{commit_id}:{bug_name}' for commit_id, bug_name in data.items()]
    save_data_to_file(path, '\n'.join(text))


def save_list_dict_to_file(path, data: dict):
    text = [f'{key}:{"|".join(value)}' for key, value in data.items()]
    save_data_to_file(path, '\n'.join(text))


def read_dict_from_file(path):
    dict_var = {}
    for line in read_data_from_file(path):
        ss = line.strip().split(':')
        dict_var[ss[0]] = ss[1]
    return dict_var


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
    return target_line.endswith(')') \
           or target_line.startswith('//') \
           or target_line.startswith('/*') \
           or target_line.startswith('*') \
           or target_line.endswith('*/')


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
