# -*-coding:utf-8-*-

import logging
from helper.git_helper import *
from helper.diff_helper import parse_diff, get_version_line


def get_version_info(project):
    """
    OK.
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
    next_version_time = datetime.datetime.strptime(next_version_date, '%a %b %d %H:%M:%S %Y %z')
    exclude_result = [result[0]] + [r for r in result[1:] if get_time(r.split(',')[3]) < next_version_time]
    return exclude_result


def assign_bugs_for_each_version(project, branch_name):
    """
    Algorithm 2
    :return:
    """
    branch_info = load_branch_dict(project)
    os.chdir(code_repos_paths[project])
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    diff_temp_path = f'{analysis_file_path}/diff_temp.txt'
    # 待测版本的commit id and version name
    lines = read_data_from_file(f'{analysis_file_path}/bug_commits_lines_info.csv')
    commit_version_name, commit_version_date, commit_version_next, commit_version_branch = get_version_info(project)
    for commit_version_id, version_name in commit_version_name.items():

        result = ["buggy file,buggy_line_in_the_version,bug_inducing_commit,bug_fixing_commit"]

        for index in range(len(lines[1:])):
            print(f'Processing {version_name}： {index}/{len(lines[1:])}')
            # [commit_id, bug_file, bug_line, inducing commit]
            temp = lines[1:][index].strip().split(',')
            bug_fixing_commit = temp[0]
            buggy_file = temp[1]
            bug_line_in_previous_commit = temp[2]
            bug_inducing_commit = temp[3]

            if bug_inducing_commit.startswith('^'):
                bug_inducing_commit = bug_inducing_commit[1:]

            if commit_version_id not in commit_dict_hashcode_index.keys():
                print('version commit id is not in the branch')
                continue
            if bug_inducing_commit not in branch_info:
                continue

            if commit_version_branch[commit_version_id] not in branch_info[bug_inducing_commit]:
                continue
            # 当前版本的commit在 BIC commit和 BFC commit之间 after commitStart and before commit_id 之间的时期为bug生存期
            # && bug_fixing_commit should older than test release data
            if get_time(bug_inducing_commit) <= get_time(commit_version_id) < get_time(bug_fixing_commit):
                # Checking the diff between a bug commit and the specific version k
                # the bug lines in Vm must can be founded in Vt
                cmd = f'git diff {bug_fixing_commit}~1 {commit_version_id} -- {buggy_file} > {diff_temp_path}'
                os.system(cmd)

                diff = read_data_from_file(diff_temp_path)
                # We need to relocate the target lines when temp diff file is not empty.
                if os.path.getsize(diff_temp_path):
                    try:
                        version_diff = parse_diff(diff)

                        # 当解析前后的版本中文件路径发生变更时，暂不考虑
                        if version_diff[0].tar_file == "/dev/null":
                            continue
                        del_lines = version_diff[0].hunk_infos['d']
                        add_lines = version_diff[0].hunk_infos['a']
                        bug_line_in_version = get_version_line(del_lines, add_lines, int(bug_line_in_previous_commit))

                    except:
                        logging.warning("Cannot analyze diff")
                        continue
                # There is no change between the target version and the last bug-containing commmit
                # when temp diff file is empty. Thus, directly assign.
                else:
                    bug_line_in_version = bug_line_in_previous_commit

                result.append(f'{buggy_file},{bug_line_in_version},{bug_inducing_commit},{bug_fixing_commit}')
        # save line level defect dataset
        dataset_path = f'{dataset_paths[project]}/{branch_name}'
        make_path(dataset_path)
        save_data_to_file(f'{dataset_path}/{version_name}_defective_lines_dataset.csv', '\n'.join(result))
        result = exclude_bugs_fixed_after_next_version(result, commit_version_next[commit_version_id])
        save_data_to_file(f'{dataset_path}/{version_name}_tmp_defective_lines_dataset.csv', '\n'.join(result))


if __name__ == '__main__':

    for proj in projects:
        get_commit_info(proj)
        assign_bugs_for_each_version(proj)
