# -*-coding:utf-8-*-

import logging
from helper.git_helper import *
from helper.diff_helper import *

tmp_dict = {}


def get_version_info(project):
    """
    Get version information. commit id, version name, version date, next date, branch. OK.
    :return:
    """
    commit_version_name, commit_version_date, commit_version_next, commit_version_branch = {}, {}, {}, {}
    lines = read_data_from_file(version_file_paths[project])
    for line in lines[1:]:
        spices = line.strip().split(",")
        commit_id = spices[0]
        commit_version_name[commit_id] = spices[1]
        commit_version_date[commit_id] = spices[2]
        commit_version_next[commit_id] = spices[3]
        commit_version_branch[commit_id] = spices[4]

    return commit_version_name, commit_version_date, commit_version_next, commit_version_branch


def exclude_bugs_fixed_after_next_version(result, next_version_date):
    """
    Filter the bugs that fixed before next version. OK
    :param result:
    :param next_version_date:
    :return:
    """
    next_version_time = datetime.datetime.strptime(next_version_date, '%a %b %d %H:%M:%S %Y %z')
    exclude_result = [result[0]] + [r for r in result[1:] if c_to_time[r.split(',')[3]] < next_version_time]
    return exclude_result


def transform(commit):
    if commit.startswith('^'):
        bic_commit = commit[1:]
        if bic_commit in tmp_dict:
            return tmp_dict[bic_commit]
        for x in commit_all:
            if x.startswith(bic_commit):
                tmp_dict[bic_commit] = x
                return x
    else:
        return commit


def main_step_assign_bugs_for_each_version(project, branch_name, analysis_file_path):
    """
    Assigning the bugs for each version. OK
    :param project:
    :param branch_name:
    :param analysis_file_path:
    :return:
    """

    branch_dict = load_pk_result(f'{analysis_file_paths[project]}/branch_dict.pk')
    diff_temp_path = f'{analysis_file_path}/diff_temp.txt'
    branch_name = branch_name.replace("/", "-")
    print(branch_name)
    dataset_path = f'{dataset_paths[project]}/{branch_name}'

    make_path(dataset_path)
    last_cmd, diff = '', ''
    # 待测版本的commit id and version name
    lines = read_data_from_file(f'{analysis_file_path}/bug_commits_lines_info.csv')
    version_name, v_date, v_next_date, v_to_branch = get_version_info(project)
    for v_id, v_name in version_name.items():
        result = ["buggy file,buggy_line_in_the_version,bug_inducing_commit,bug_fixing_commit"]
        result_path = f'{dataset_path}/{v_name}_defective_lines_dataset.csv'
        tmp_result_path = f'{dataset_path}/{v_name}_tmp_defective_lines_dataset.csv'
        if os.path.exists(result_path):
            continue

        for index in range(len(lines[1:])):
            print(f'Processing {v_name}： {index}/{len(lines[1:])}') if index % 500 == 0 else None
            temp = lines[1:][index].strip().split(',')
            bfc_commit, bic_commit = temp[0], transform(temp[3])
            buggy_file, bug_line_in_last_commit = temp[1], int(temp[2])
            bic_branch = []
            if bic_commit not in c_to_branches:
                continue
            for b in c_to_branches[bic_commit]:
                bic_branch += branch_dict[b]
            if v_to_branch[v_id] not in bic_branch:
                # print(f' version and BIC are not in the same branch')
                continue

            if v_id not in commit_all:
                # print(f' version commit is not in the current branch {branch_name}')
                # 这种情况最好不应该跳过，而是应该另外处理 版本的时间在BIC和BFC之间,先找到BIC的行, 版本的行
                continue
            # 当前版本的commit在 BIC commit和 BFC commit之间 after commitStart and before commit_id 之间的时期为bug生存期
            # && bug_fixing_commit should older than test release data
            if c_to_time[bic_commit] <= c_to_time[v_id] < c_to_time[bfc_commit]:
                # Checking the diff between a bug commit and the specific version k
                # the bug lines in Vm must can be founded in Vt

                cmd = f'git diff {bfc_commit}~1 {v_id} -- {buggy_file} > {diff_temp_path}'
                if cmd != last_cmd:
                    os.system(cmd)
                    diff = read_data_from_file(diff_temp_path)
                    last_cmd = cmd

                # We need to relocate the target lines when temp diff file is not empty.
                if os.path.getsize(diff_temp_path):
                    version_diff = parse_diff(diff)
                    # Ignoring the files whose paths change before and after the commit
                    if len(version_diff) == 0 or version_diff[0].tar_file == "/dev/null":
                        continue
                    del_lines = version_diff[0].hunk_info['d']
                    add_lines = version_diff[0].hunk_info['a']
                    bug_line_in_version = get_version_line(del_lines, add_lines, bug_line_in_last_commit)

                # There is no change between the target version and the last bug-containing commit
                # when temp diff file is empty. Thus, directly assign.
                else:
                    bug_line_in_version = bug_line_in_last_commit

                if bug_line_in_version != -1:
                    result.append(f'{buggy_file},{bug_line_in_version},{bic_commit},{bfc_commit}')

        # save line level defect dataset # make tmp dataset
        save_data_to_file(result_path, '\n'.join(result))
        tmp_result = exclude_bugs_fixed_after_next_version(result, v_next_date[v_id])
        save_data_to_file(tmp_result_path, '\n'.join(tmp_result))


def combine_bug_info_from_all_branch(project):
    commit_version_name, commit_version_date, commit_version_next, commit_version_branch = get_version_info(project)
    for id, version in commit_version_name.items():
        buggy_files = []
        buggy_lines = []
        for branch in os.listdir(f'{dataset_paths[project]}'):
            if str(branch).endswith('.csv'):
                continue
            dataset_path = f'{dataset_paths[project]}/{branch}/{version}_defective_lines_dataset.csv'
            lines = read_data_from_file(dataset_path)
            for line in lines[1:]:
                buggy_file = line.split(',')[0]
                buggy_line = buggy_file + ',' + line.split(',')[1]
                # buggy_line = line
                if buggy_file not in buggy_files:
                    buggy_files.append(buggy_file)
                if buggy_line not in buggy_lines:
                    buggy_lines.append(buggy_line)

        if len(buggy_files) == 0:
            continue
        branch_name = commit_version_branch[id]
        os.system(rf'git checkout -f {branch_name}')
        os.system(rf'git reset --hard {id}')
        all_file_list = export_all_files_in_project(code_repos_paths[project] + '/')

        folder_line_level = f'{root_path}/Dataset/Line-level/'
        folder_file_level = f'{root_path}/Dataset/File-level/'
        make_path(folder_line_level)
        make_path(folder_file_level)

        buggy_files = []
        line_dataset_path = f'{folder_line_level}{version.replace("/", "-")}_defective_lines_dataset.csv'
        line_dataset_text = 'File,Line_number,SRC\n'
        for buggy_line in buggy_lines:
            file_name, line_number = buggy_line.split(',')[0], int(buggy_line.split(',')[1])
            if file_name not in all_file_list:
                continue
            file_content = read_data_from_file(f'{code_repos_paths[project]}/{file_name}')
            if line_number > len(file_content):
                continue
            line_content = file_content[line_number - 1]
            if is_comment_line2(line_content):
                continue
            if buggy_line.strip().split(',')[0] not in buggy_files:
                buggy_files.append(buggy_line.strip().split(',')[0])
            line_dataset_text += buggy_line.strip() + ',' + line_content.strip() + '\n'
        save_data_to_file(line_dataset_path, line_dataset_text)

        file_dataset_path = f'{folder_file_level}/{version.replace("/", "-")}_ground-truth-files_dataset.csv'
        file_dataset_text = 'File,Bug,SRC\n'
        for file_name in all_file_list:
            file_label = 'true' if file_name in buggy_files else 'false'
            file_content = read_data_from_file(f'{code_repos_paths[project]}/{file_name}')
            file_dataset_text += file_name + ',' + file_label + ',"' + ''.join(file_content) + '"'
        save_data_to_file(file_dataset_path, file_dataset_text)

    print(f'{project} combined finish!')
