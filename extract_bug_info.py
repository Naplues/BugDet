# -*-coding:utf-8-*-
# The script has been tested successfully.

import re
import time
import logging
from helper import *
from diff_helper import parse_diff

global code_repository, root_path, result_root
commit_dict_hashcode_index, commit_dict_index_hashcode = {}, {}


def output_commit_id():
    """
    :return:None OK.
    """
    make_path(code_repository)
    make_path(result_root)

    # Change current directory
    os.chdir(code_repository)

    # Output different commit log information
    os.system(rf'git log --pretty=format:"%H %d" > {result_root}/commit_ref.txt')  # %H %ci | %H %s | %H %an %ae
    print('Output commit hash code!')


def output_diff_info():
    """
    Tracking the information (including # add and delete lines) of all files that are modified by each commit. OK.
    :return:None
    """
    # Change current directory
    os.chdir(code_repository)
    os.system("git config diff.renameLimit 3999")
    # --diff-filter=M 意味着只抽取 Modified 的文件, 不考虑Added Deleted等情况
    os.system(rf'git log --pretty=oneline --diff-filter=M --numstat > {result_root}/diff.txt')
    os.system("git config --unset diff.renameLimit")
    print('Output file change information!')


def get_commit_info():
    """
    Get commit dict information. OK.
    commit_dict_hashcode_index: Getting index from commit hash code
    commit_dict_index_hashcode: Getting hash code from commit index
    :return:
    """
    lines = read_data_from_file(rf'{result_root}/commit_ref.txt')

    for index in range(len(lines)):
        commit_id = lines[index].strip().split(' ')[0]
        commit_dict_hashcode_index[commit_id] = index
        commit_dict_index_hashcode[index] = commit_id


def get_bug_id_list(proj):
    """
    Read Bug ID. GROOVY-3 OK.
    :return:
    """
    bug_reports = read_data_from_file(rf'{root_path}/BugReport/statistics/{proj}.csv')
    bug_id_list = [bug.strip().split(',')[1] for bug in bug_reports[1:]]
    return bug_id_list


def check_bug_exist(commit_log, pattern):
    """
    :param commit_log: OK.
    :param pattern:
    :return:
    """
    match = re.search(rf"{proj.upper()}-\d+", commit_log)
    if not match:
        return False, ""
    else:
        matcher = match.group()
        if matcher in pattern:
            return True, matcher
        else:
            return False, ""


def output_commit_bug_files_map(proj):
    """
    # OK 获取commit 和 bug 对应表
    Match a bug id, its bug files, and its bug-fixing commit
    :return:
    """
    lines = read_data_from_file(rf'{result_root}/diff.txt')
    # [commit_id,  bug id, changed files, commit log]
    commit_bug_files_map, content_of_prev_commit, last_commit_is_bug = [], [], False

    bug_id_list = get_bug_id_list(proj)  # 获取所有bug id作为待匹配模式

    # 逐行解析处理diff.txt文件
    for line in lines:
        tmp = line.split("\t", 2)
        if len(tmp) != 1 and len(tmp) != 3:
            continue
        # When processing a new commit id line
        if len(tmp) != 3:
            # save the last commit info 对第一条记录直接跳过
            commit_bug_files_map.append(content_of_prev_commit) if last_commit_is_bug else None
            # Processing the current commit
            commit_id, commit_log = line[:40], line[40:]
            # 检查该日志中是否含有bug修复信息
            last_commit_is_bug, bug_id = check_bug_exist(commit_log, bug_id_list)
            if not last_commit_is_bug:
                continue
            content_of_prev_commit = [commit_id, bug_id, [], commit_log]

        # 文件change 行: 只添加包含bug的commit中的java文件
        if len(tmp) == 3 and last_commit_is_bug:  # and tmp[2].endswith('.java'):  TODO
            content_of_prev_commit[2].append(tmp[2])  # tmp[2]: java files

    # save the last commit info
    commit_bug_files_map.append(content_of_prev_commit) if last_commit_is_bug else None
    result = ''.join([f'{d[0]},{d[1]},{d[3]}' for d in commit_bug_files_map])
    save_data_to_file(f'{result_root}/commit_id_bug_log.csv', result)
    dump_pk_result(f'{result_root}/commit_id_bug_files.pk', commit_bug_files_map)
    print('Output and get commit bug files map!')
    return commit_bug_files_map


def get_commit_bug_files_map():
    commit_id_bug_files_path = f'{result_root}/commit_id_bug_files.pk'
    pk_data = load_pk_result(commit_id_bug_files_path)
    csv_data = read_data_from_file(f'{result_root}/commit_id_bug_log.csv')
    # Select the commits id that have been identified by humans
    commit_ids = [line.split(',')[0] for line in csv_data]
    pk_data = [c for c in pk_data if c[0] in commit_ids]
    return pk_data


def output_bug_fixing_commit_diff():
    """
    Output bug-fixing commit diff file. OK.
    :return:
    """
    # Change current directory
    os.chdir(code_repository)

    commit_bug_files_map = get_commit_bug_files_map()
    make_path(f'{result_root}/diff/')

    for index in range(len(commit_bug_files_map)):
        commit_id = commit_bug_files_map[index][0]
        # --full-index TODO 是否需要忽略空白行-B
        os.system(f'git log -p -n 1 --full-index {commit_id} > {result_root}/diff/{commit_id}.txt')
        print(f'{index}/{len(commit_bug_files_map)}')


def identify_bug_inducing_commit(src_file, del_lines):
    """
    Leverage delete file lines in src file (i.e., buggy lines) to identifying bug-inducing commits
    :param src_file:
    :param del_lines:
    :return:
    """
    # Change current directory
    os.chdir(code_repository)

    make_path(f'{result_root}/blame/')
    blame_file_path = f'{result_root}/blame/{src_file.replace("/", ".")}.txt'
    os.system(f'git blame --abbrev=7 {src_file} > {blame_file_path}')
    blame_file = read_data_from_file(blame_file_path)
    bug_inducing_commit = []
    for line in del_lines:
        # Skip if the line number is greater than the size of the file
        if line > len(blame_file):
            logging.warning(f'git blame line error! {src_file}:{line}:{len(blame_file)}')
            continue
        # Skip if it is a blank line
        if blame_file[line - 1].strip().endswith(")"):
            continue
        # Otherwise, processing the line that was deleted
        tmps = re.split("\s+", blame_file[line - 1].strip())
        # [line number, line_inducing_commit_id]
        bug_inducing_commit.append([line, tmps[0]]) if len(tmps) > 0 else None

    return bug_inducing_commit


def resolve_diff_file():
    """
    Identifying defective file lines by tracking bug fixing commit. OK.
    :return:
    """
    # Change current directory
    os.chdir(code_repository)

    result_text = ''
    for commit_instance in get_commit_bug_files_map():
        bug_fixing_commit_id = commit_instance[0]  # bug fixing commit

        os.chdir(code_repository)
        os.system(f'git reset --hard {bug_fixing_commit_id}~1')  # 定位到修复前一个commit(i.e., 包含bug的最后一个commit)

        diff = read_data_from_file(f'{result_root}/diff/{bug_fixing_commit_id}.txt')
        try:
            bug_file_info = parse_diff(diff)
        except:
            logging.warning("Cannot analyze diff " + result_root + "diff/" + bug_fixing_commit_id + ".txt")
            continue

        # Processing the deleted lines in each changed file
        for bug_file in bug_file_info:
            bug_lines_delete = bug_file.hunk_infos['d']
            src_file = bug_file.src_file[2:]  # remove a/ to get the original file path
            # Skip if it is not a java file or there is no deleted lines
            if not src_file.endswith('.java') or len(bug_lines_delete) == 0:
                continue

            # the bug lines are introduced in their corresponding commits
            for instance in identify_bug_inducing_commit(src_file, bug_lines_delete):
                line_in_previous_commit = str(instance[0])
                line_inducing_commit_id = instance[1]
                result_text += f'{bug_fixing_commit_id},{src_file},{line_in_previous_commit},{line_inducing_commit_id}\n'

    save_data_to_file(f'{result_root}/bug_commits_lines_info.csv', result_text)
    os.system(f'git reset --hard {commit_dict_index_hashcode[0]}')


if __name__ == '__main__':
    # Processing each project
    for proj in projects:
        code_repository = root_path + "/Repository/" + proj
        result_root = root_path + "/Result/Bug/" + proj

        # output_commit_log()
        # output_diff_info()
        get_commit_info()

        # output_commit_bug_files_map(proj)
        # Manually remove non-bugs commit TODO need review manually

        # output_bug_fixing_commit_diff()
        resolve_diff_file()
