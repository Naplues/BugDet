# -*-coding:utf-8-*-
# The script has been tested successfully.

import datetime
from helper.file_helper import *

# All commits in a branch
commit_all = []
all_bug_fixing_commit = []

c_to_time = {}
c_to_branches = {}


def selected_branches(project):
    """
    Output the branches that we need process. OK
    :param project:
    :return:
    """
    branch_file = f'{analysis_file_paths[project]}/branch.txt'

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! run the below code only once !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # checkout remote branches
    # os.system(rf'git branch -r > {branch_file}')
    # file = read_data_from_file(branch_file)
    # for branch in [line.split('origin/')[-1].strip() for line in file[1:]]:
    #     print(f'Processing {project} {branch}')
    #     os.system(rf'git checkout -f {branch}')
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!! run the above code only once !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    if not os.path.exists(branch_file):
        # filter the merged branches
        os.system(rf'git branch > {branch_file}')
        file = read_data_from_file(branch_file)
        temp_file = f'{analysis_file_paths[project]}/temp.txt'
        branch_name_list = [line.replace('*', '').strip() for line in file]
        removed_branch_list = []
        branch_dict = {}
        for branch_name in branch_name_list:
            os.system(rf'git branch --merged {branch_name} > {temp_file}')
            branch_dict[branch_name] = [element.replace('*', '').strip() for element in read_data_from_file(temp_file)]
            merged_branch = [element.replace('*', '').strip() for element in read_data_from_file(temp_file)]
            merged_branch.remove(branch_name)
            removed_branch_list += merged_branch

        removed_branch_list = list(set(removed_branch_list))
        remained_branch_list = [branch for branch in branch_name_list if branch not in removed_branch_list]
        print(len(branch_name_list), branch_name_list)
        os.remove(temp_file)
        save_data_to_file(branch_file, '\n'.join(remained_branch_list))
        dump_pk_result(f'{analysis_file_paths[project]}/branch_dict.pk', branch_dict)

    # the branch that we need
    remained_branch_list = [line.strip() for line in read_data_from_file(branch_file)]
    print(f'{len(remained_branch_list)} branches need to be processed in {project}. {remained_branch_list}.')
    return remained_branch_list


def output_commit_info(branch_name, analysis_file_path):
    """
    Output all commit information for each branch
    :param branch_name:
    :param analysis_file_path:
    :return:
    """
    os.system(rf'git checkout -f {branch_name}')
    if not os.path.exists(f'{analysis_file_path}/commit_ref.txt'):
        # Output different commit log information   # %H %ci | %H %s | %H %an %ae
        os.system(rf'git log --pretty=format:"%H|%cd|%s" > {analysis_file_path}/commit_ref.txt')
    print(f'Output commit hash code! {"=" * 50}')


def output_diff_info(analysis_file_path):
    """
    Tracking the information (including # add and delete lines) of all files that are modified by each commit. OK.
    :return:None
    """

    if not os.path.exists(f'{analysis_file_path}/diff.txt'):
        os.system("git config diff.renameLimit 3999")
        # --diff-filter=M: Files were modified rather than were added or deleted by a diff will be considered.
        os.system(rf'git log --pretty=oneline --diff-filter=M --numstat > {analysis_file_path}/diff.txt')
        os.system("git config --unset diff.renameLimit")
    print(f'Output file change information! {"=" * 50}')


def get_commit_info(branch_name, analysis_file_path):
    """
    Get commit dict information. OK.
    :param branch_name:
    :param analysis_file_path:
    :return:
    """
    output_commit_info(branch_name, analysis_file_path)
    output_diff_info(analysis_file_path)

    commit_all = []
    lines = read_data_from_file(rf'{analysis_file_path}/commit_ref.txt')
    for index in range(len(lines)):
        commit_id = lines[index].strip().split('|')[0]
        commit_time = lines[index].strip().split('|')[1]
        commit_all.append(commit_id)
        c_to_time[commit_id] = datetime.datetime.strptime(commit_time, '%a %b %d %H:%M:%S %Y %z')


def load_commit_branch_dict(project):
    """
    Looking the branches that commit exists. [commit id -> branch list] OK.
    :param project:
    :return:
    """
    for branch in [line.strip() for line in read_data_from_file(f'{analysis_file_paths[project]}/branch.txt')]:
        lines = read_data_from_file(rf'{analysis_file_paths[project]}/{branch}/commit_ref.txt')
        for line in lines:
            commit_id = line.strip().split('|')[0]
            if commit_id not in c_to_branches:
                c_to_branches[commit_id] = [branch]
            else:
                c_to_branches[commit_id].append(branch)
    return c_to_branches


if __name__ == '__main__':
    load_commit_branch_dict('cassandra')
