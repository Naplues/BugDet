# -*-coding:utf-8-*-
# The script has been tested successfully.

import datetime

from helper.config import *
from helper.file_helper import *
from pprint import *

# All commits in a branch
commit_all = []
all_bug_fixing_commit = []
# commit id -> commit time
# commit id -> branch
c_to_time = {}
c_to_branches = {}


############################# Processing branch information ====================================
def checkout_all_remote_branches(project):
    """
    Checkout all branches from remote origin server to local machine.
    :param project: The processed project
    :return:
    """
    make_path(analysis_file_paths[project])
    # Root/DataCollection/Analysis/ambari/branch.txt
    branch_file = f'{analysis_file_paths[project]}/branch-remote.txt'
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! run the below code only once !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Checkout remote branches
    if not os.path.exists(branch_file):
        # 导出远程版本库中存在的分支名称列表到文件 Root/DataCollection/Analysis/ambari/branch.txt 中
        os.system(rf'git branch -r > {branch_file}')
        file = read_data_from_file(branch_file)
        print(file)
        for branch in [line.split('origin/')[-1].strip() for line in file[1:]]:
            print(f'Checking out the branch {project} {branch} from remote origin server.')
            os.system(rf'git checkout -f {branch}')
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! run the above code only once !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def load_selected_branches(project: str):
    """
    Output the branches that we need process. OK
    :param project:
    :return:
    """

    checkout_all_remote_branches(project)

    make_path(analysis_file_paths[project])
    branch_file = f'{analysis_file_paths[project]}/branch.txt'

    if not os.path.exists(branch_file):
        print('Selecting proper branches......')
        branch_file_local = f'{analysis_file_paths[project]}/branch-local.txt'
        # Filter the merged branches
        os.system(rf'git branch > {branch_file_local}')
        temp_file = f'{analysis_file_paths[project]}/temp.txt'
        branch_name_list = [line.replace('*', '').strip() for line in read_data_from_file(branch_file_local)]
        removed_branch_list = []
        branch_dict = {}
        for branch_name in branch_name_list:
            # 已被并入当前分支的所有分支们,这些分支属冗余分支,应当被移除,在之后的操作中不考虑它们
            os.system(rf'git branch --merged {branch_name} > {temp_file}')

            merged_branch = [e.replace('*', '').replace(',', '').strip() for e in read_data_from_file(temp_file)]
            branch_dict[branch_name] = list(merged_branch)
            merged_branch.remove(branch_name) if branch_name in merged_branch else None
            removed_branch_list += merged_branch

        removed_branch_list = list(set(removed_branch_list))
        remained_branch_list = [branch for branch in branch_name_list if branch not in removed_branch_list]

        os.remove(temp_file)
        save_data_to_file(branch_file, '\n'.join(remained_branch_list))
        save_data_to_file(f'{analysis_file_paths[project]}/branch_merge_dict.txt', pformat(branch_dict))
        dump_pk_result(f'{analysis_file_paths[project]}/branch_merge_dict.pk', branch_dict)

    # The branch that we need
    remained_branch_list = [line.strip() for line in read_data_from_file(branch_file)]

    print('=' * 20 + f' {len(remained_branch_list)} available branches in project {project.upper()} ' + '=' * 20)
    pprint(remained_branch_list)
    print('=' * 20 + f' {len(remained_branch_list)} available branches in project {project.upper()} ' + '=' * 20 + '\n')

    return remained_branch_list


############################# Export commit information ====================================
def export_commit_info(branch_name, analysis_file_path):
    """
    Output all commit information for each branch
    """
    if not os.path.exists(f'{analysis_file_path}/commit_ref.txt'):
        os.system(rf'git checkout -f {branch_name}')
        # Export different commit log information   # %H %ci | %H %s | %H %an %ae
        os.system(rf'git log --pretty=format:"%H|%cd|%s" > {analysis_file_path}/commit_ref.txt')
        print(f'========== Export commit hash code for branch {branch_name}.')


def export_diff_info(branch_name, analysis_file_path):
    """
    Tracking the information (including # add and delete lines) of all files that are modified by each commit. OK.
    """
    diff_file_path = f'{analysis_file_path}/diff.txt'
    if not os.path.exists(diff_file_path):
        os.system(rf'git checkout -f {branch_name}')
        os.system("git config diff.renameLimit 3999")
        # --diff-filter=M: Files were modified rather than were added or deleted by a diff will be considered.
        os.system(rf'git log --pretty=oneline --diff-filter=M --numstat > {diff_file_path}')
        os.system("git config --unset diff.renameLimit")
        print(f'========== Export file change information diff.txt for branch{branch_name}.')


############################# Loading commit information ====================================
def load_commit_branch_dict(project, branches):
    """
    Looking the branches that commit exists. [commit id -> branch list] OK.
    """
    # 没有考虑被移除的分支,因此可能
    for branch in branches:
        # 读取该分支下的所有commit hash id
        for line in read_data_from_file(rf'{analysis_file_paths[project]}/{branch}/commit_ref.txt'):
            commit_id = line.strip().split('|')[0]
            if commit_id not in c_to_branches:
                c_to_branches[commit_id] = [branch]
            else:
                c_to_branches[commit_id].append(branch)


def load_commit_info(analysis_file_path):
    """
    Get commit dict information. OK.
    """
    commit_all.clear()
    lines = read_data_from_file(rf'{analysis_file_path}/commit_ref.txt')
    for index in range(len(lines)):
        commit_id = lines[index].strip().split('|')[0]
        commit_time = lines[index].strip().split('|')[1]
        commit_all.append(commit_id)
        c_to_time[commit_id] = datetime.datetime.strptime(commit_time, '%a %b %d %H:%M:%S %Y %z')
    print("===== The info (commit_all, commit id -> commit time) has been loaded.")
