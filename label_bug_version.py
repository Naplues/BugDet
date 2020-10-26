# -*-coding:utf-8-*-

import re
import logging
from helper.file_helper import *
from helper.diff_helper import parse_diff, get_version_line

global project, branch_name

commit_dict_hashcode_index = {}
commit_all = []


def get_version_commit_id_and_name():
    """
    OK.
    :return:
    """
    commit_version_dict = {}
    lines = read_data_from_file(version_root)
    for line in lines[1:]:
        spices = line.strip().split(",")
        commit_id = spices[0][:8]
        commit_version_name = spices[1]
        commit_version_dict[commit_id] = commit_version_name

    return commit_version_dict


def get_commit_info():
    """
    OK.
    """
    lines = read_data_from_file(f'{result_root}/commit_ref.txt')
    for index in range(len(lines)):
        line = re.split("\s+", lines[index].strip())
        commit_dict_hashcode_index[line[0][:8]] = index
        commit_all.append(line[0][:8])


def get_commit_version():
    """
    Algorithm 2
    :return:
    """
    lines = read_data_from_file(f'{result_root}/bug_commits_lines_info.csv')
    os.chdir(code_repository)
    result = ["target version, bug line in target version, bug line in last commit, "
              "bug-inducing commit, bug-fixing commit, bug file path"
              ]
    cmd_temp = ""

    diff_temp_path = f'{result_root}/diff_temp.txt'
    # 待测版本的commit id and version name
    for version_commit, version_name in get_version_commit_id_and_name().items():
        print(f'Processing {version_name}')

        for index in range(len(lines[1:])):
            print(f'{index}/{len(lines[1:])}')
            # [commit_id, bug_file, bug_line, inducing commit]
            temp = lines[1:][index].strip().split(",")
            bug_line_fixing_commit_id = temp[0][:8]
            bug_file_path = temp[1]
            bug_line_in_previous_commit = temp[2]
            bug_line_inducing_commit = temp[3]

            if bug_line_inducing_commit.startswith('^'):
                for c in commit_all:
                    if bug_line_inducing_commit == ('^' + c[0:7]):
                        bug_line_inducing_commit = c
                        break

            if bug_line_inducing_commit not in commit_dict_hashcode_index.keys():
                logging.warning("Can not find the commit_id: " + bug_line_inducing_commit)
                continue

            if version_commit not in commit_dict_hashcode_index.keys():
                continue

            version_index = commit_dict_hashcode_index[version_commit]
            bug_inducing_index = commit_dict_hashcode_index[bug_line_inducing_commit]
            bug_fixing_index = commit_dict_hashcode_index[bug_line_fixing_commit_id]
            # 9 [8] 7 [6] 5 4 [3] 2 1
            # 当前版本的commit在 引入bug的commit和修复bug的commit之间 after commitStart and before commit_id 之间的时期为bug生存期

            if bug_inducing_index >= version_index > bug_fixing_index:
                # Checking the diff between a bug commit and the specific version k
                # the bug lines in Vm must can be founded in Vt
                cmd = f'git diff {bug_line_fixing_commit_id}~1 {version_commit} -- {bug_file_path} > {diff_temp_path}'
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

                result.append(""
                              + version_name + ","
                              + str(bug_line_in_version) + ", "
                              + bug_line_in_previous_commit + ","
                              + bug_line_inducing_commit + ","
                              + bug_line_fixing_commit_id + ","
                              + bug_file_path + ","
                              )
    # bug在指定版本的文件及行号
    save_data_to_file(f'{result_root}/result.csv', '\n'.join(result))


if __name__ == '__main__':

    for proj in projects:
        project = proj
        code_repository = root_path + "/Repository/" + project + "/"
        result_root = root_path + "/Result/Bug/" + project + "/"
        version_root = root_path + "/Version/" + project + ".csv"

        get_commit_info()
        get_commit_version()
