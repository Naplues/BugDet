# -*-coding:utf-8-*-
# The script has been tested successfully.

import datetime
from helper.file_helper import *

commit_all = []
commit_dict_hashcode_index, commit_dict_index_hashcode, commit_dict_hashcode_time = {}, {}, {}


def output_branch_info(project):
    """
    :return:None OK.
    """
    make_path(code_repos_paths[project])
    make_path(analysis_file_paths[project])

    # Change current directory
    os.chdir(code_repos_paths[project])

    # Output different commit log information   # %H %ci | %H %s | %H %an %ae
    '''
    # run the below code only once
    os.system(rf'git branch -r > {analysis_file_paths[project]}/branch.txt')
    file = read_data_from_file(f'{analysis_file_paths[project]}/branch.txt')
    remote_branch = [line.split('origin/')[-1].strip() for line in file[1:]]
    for branch in remote_branch:
        print(f'Processing {project} {branch}')
        os.system(rf'git checkout -f {branch}')
    '''

    os.system(rf'git branch > {analysis_file_paths[project]}/branch.txt')
    file = read_data_from_file(f'{analysis_file_paths[project]}/branch.txt')
    branch_name = [line.replace('*', '').strip() for line in file]
    save_data_to_file(f'{analysis_file_paths[project]}/branch.txt', '\n'.join(branch_name))
    print(f'Output branch information for {project}!')
    return branch_name


def output_commit_info(project, branch_name):
    """
    :return:None OK.
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    make_path(code_repos_paths[project])
    make_path(analysis_file_path)

    # Change current directory
    os.chdir(code_repos_paths[project])
    os.system(rf'git checkout -f {branch_name}')
    # Output different commit log information   # %H %ci | %H %s | %H %an %ae
    os.system(rf'git log --pretty=format:"%H|%cd" > {analysis_file_path}/commit_ref.txt')
    print('Output commit hash code!')


def output_diff_info(project, branch_name):
    """
    Tracking the information (including # add and delete lines) of all files that are modified by each commit. OK.
    :return:None
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    # Change current directory
    os.chdir(code_repos_paths[project])
    os.system("git config diff.renameLimit 3999")
    # --diff-filter=M 意味着只抽取 Modified 的文件, 不考虑Added Deleted等情况
    os.system(rf'git log --pretty=oneline --diff-filter=M --numstat > {analysis_file_path}/diff.txt')
    os.system("git config --unset diff.renameLimit")
    print('Output file change information!')


def get_commit_info(project, branch_name):
    """
    Get commit dict information. OK.
    commit_dict_hashcode_index: Getting index from commit hash code
    commit_dict_index_hashcode: Getting hash code from commit index
    :return:
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    output_commit_info(project, branch_name)
    output_diff_info(project, branch_name)
    lines = read_data_from_file(rf'{analysis_file_path}/commit_ref.txt')
    for index in range(len(lines)):
        commit_id = lines[index].strip().split('|')[0]
        commit_time = lines[index].strip().split('|')[1]
        commit_all.append(commit_id)
        commit_dict_hashcode_index[commit_id] = index
        commit_dict_index_hashcode[index] = commit_id
        commit_dict_hashcode_time[commit_id] = datetime.datetime.strptime(commit_time, '%a %b %d %H:%M:%S %Y %z')


def get_time(commit_id):
    return commit_dict_hashcode_time[commit_id]
