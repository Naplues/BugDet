# -*-coding:utf-8-*-
# The script has been tested successfully.

import datetime
from helper.file_helper import *
from pprint import pprint

commit_all = []
all_bug_fixing_commit = []
commit_all_branch_dict = {}
commit_dict_hashcode_index, commit_dict_index_hashcode, commit_dict_hashcode_time = {}, {}, {}


def output_branch_info(project):
    """
    Output the branches that we need process. OK
    :param project:
    :return:
    """
    make_path(code_repos_paths[project])
    make_path(analysis_file_paths[project])

    # Change current directory
    os.chdir(code_repos_paths[project])

    branch_file = f'{analysis_file_paths[project]}/branch.txt'

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! run the below code only once !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # checkout remote branches
    # os.system(rf'git branch -r > {branch_file}')
    # file = read_data_from_file(branch_file)
    # for branch in [line.split('origin/')[-1].strip() for line in file[1:]]:
    #     print(f'Processing {project} {branch}')
    #     os.system(rf'git checkout -f {branch}')
    #
    # # filter the merged branches
    # os.system(rf'git branch > {branch_file}')
    # file = read_data_from_file(branch_file)
    # temp_file = f'{analysis_file_paths[project]}/temp.txt'
    # branch_name_list = [line.replace('*', '').strip() for line in file]
    # removed_branch_list = []
    # for branch_name in branch_name_list:
    #     os.system(rf'git branch --merged {branch_name} > {temp_file}')
    #     merged_branch = [element.replace('*', '').strip() for element in read_data_from_file(temp_file)]
    #     merged_branch.remove(branch_name)
    #     removed_branch_list += merged_branch
    #
    # removed_branch_list = list(set(removed_branch_list))
    # remained_branch_list = [branch for branch in branch_name_list if branch not in removed_branch_list]
    # print(len(branch_name_list), branch_name_list)
    # os.remove(temp_file)
    # save_data_to_file(branch_file, '\n'.join(remained_branch_list))
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! run the above code only once !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # the branch that we need
    remained_branch_list = [line.strip() for line in read_data_from_file(branch_file)]
    print(f'{len(remained_branch_list)} branches need to be processed in {project}. {remained_branch_list}.')
    return remained_branch_list


def output_commit_info(project, branch_name):
    """
    :return:None OK.
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    make_path(analysis_file_path)

    if not os.path.exists(f'{analysis_file_path}/commit_ref.txt'):
        # Change current directory
        os.chdir(code_repos_paths[project])
        os.system(rf'git checkout -f {branch_name}')
        # Output different commit log information   # %H %ci | %H %s | %H %an %ae
        os.system(rf'git log --pretty=format:"%H|%cd|%s" > {analysis_file_path}/commit_ref.txt')
    print(f'Output commit hash code! {"=" * 50}')


def output_diff_info(project, branch_name):
    """
    Tracking the information (including # add and delete lines) of all files that are modified by each commit. OK.
    :return:None
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'

    if not os.path.exists(f'{analysis_file_path}/diff.txt'):
        # Change current directory
        os.chdir(code_repos_paths[project])
        os.system("git config diff.renameLimit 3999")
        # --diff-filter=M 意味着只抽取 Modified 的文件, 不考虑Added Deleted等情况
        os.system(rf'git log --pretty=oneline --diff-filter=M --numstat > {analysis_file_path}/diff.txt')
        os.system("git config --unset diff.renameLimit")
    print(f'Output file change information! {"=" * 50}')


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
        commit_all.append(commit_id)  # 可移动位置
        commit_dict_hashcode_index[commit_id] = index
        commit_dict_index_hashcode[index] = commit_id
        commit_dict_hashcode_time[commit_id] = datetime.datetime.strptime(commit_time, '%a %b %d %H:%M:%S %Y %z')


def load_commit_branch_dict(project):
    """
    Looking the branches that commit exists. OK
    :param project:
    :return:
    """
    for branch in [line.strip() for line in read_data_from_file(f'{analysis_file_paths[project]}/branch.txt')]:
        lines = read_data_from_file(rf'{analysis_file_paths[project]}/{branch}/commit_ref.txt')
        for line in lines:
            commit_id = line.strip().split('|')[0]
            if commit_id not in commit_all_branch_dict:
                commit_all_branch_dict[commit_id] = [branch]
            else:
                commit_all_branch_dict[commit_id].append(branch)
    return commit_all_branch_dict


def get_time(commit_id):
    return commit_dict_hashcode_time[commit_id]


if __name__ == '__main__':
    load_commit_branch_dict('cassandra')
