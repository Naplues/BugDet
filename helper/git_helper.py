# -*-coding:utf-8-*-
# The script has been tested successfully.

import datetime
from helper.file_helper import *

commit_all = []
commit_dict_hashcode_index, commit_dict_index_hashcode, commit_dict_hashcode_time = {}, {}, {}


def output_commit_info(project):
    """
    :return:None OK.
    """
    make_path(code_repos_paths[project])
    make_path(analysis_file_paths[project])

    # Change current directory
    os.chdir(code_repos_paths[project])

    # Output different commit log information   # %H %ci | %H %s | %H %an %ae
    os.system(rf'git log --pretty=format:"%H|%cd" > {analysis_file_paths[project]}/commit_ref.txt')
    print('Output commit hash code!')


def output_diff_info(project):
    """
    Tracking the information (including # add and delete lines) of all files that are modified by each commit. OK.
    :return:None
    """
    # Change current directory
    os.chdir(code_repos_paths[project])
    os.system("git config diff.renameLimit 3999")
    # --diff-filter=M 意味着只抽取 Modified 的文件, 不考虑Added Deleted等情况
    os.system(rf'git log --pretty=oneline --diff-filter=M --numstat > {analysis_file_paths[project]}/diff.txt')
    os.system("git config --unset diff.renameLimit")
    print('Output file change information!')


def get_commit_info(project):
    """
    Get commit dict information. OK.
    commit_dict_hashcode_index: Getting index from commit hash code
    commit_dict_index_hashcode: Getting hash code from commit index
    :return:
    """
    output_commit_info(project)
    output_diff_info(project)
    lines = read_data_from_file(rf'{analysis_file_paths[project]}/commit_ref.txt')
    for index in range(len(lines)):
        commit_id = lines[index].strip().split('|')[0]
        commit_time = lines[index].strip().split('|')[1]
        commit_all.append(commit_id)
        commit_dict_hashcode_index[commit_id] = index
        commit_dict_index_hashcode[index] = commit_id
        commit_dict_hashcode_time[commit_id] = datetime.datetime.strptime(commit_time, '%a %b %d %H:%M:%S %Y %z')


def get_time(commit_id):
    return commit_dict_hashcode_time[commit_id]


if __name__ == '__main__':

    for proj in projects:
        output_commit_info(proj)
