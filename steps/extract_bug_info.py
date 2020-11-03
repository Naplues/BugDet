# -*-coding:utf-8-*-
# The script has been tested successfully.

import re
import logging
from helper.git_helper import *
from helper.diff_helper import parse_diff


def get_bug_id_list(project):
    """
    Read Bug ID list. [GROOVY-1, GROOVY-2] OK.
    :return:
    """
    bug_reports = read_data_from_file(rf'{root_path}/BugReport/{project}.csv')
    bug_id_list = [bug.strip().split(',')[1] for bug in bug_reports[1:]]
    return bug_id_list


def match_bug_pattern(project, commit_log, pattern):
    """
    Check whether commit log matches a bug. If so, the commit is considered as a BIC (bug-fixing-commit). OK
    :param project:
    :param commit_log:
    :param pattern:
    :return:
    """
    status, matched_pattern = False, ''
    match = re.search(rf"{project.upper()}-\d+", commit_log)

    if match:
        # Match the resolved bug id in recorded in JIRA
        matcher = match.group()
        if matcher in pattern:
            status, matched_pattern = True, matcher
    else:
        # Match the number
        for bug_id in re.findall(rf'\d+', commit_log):
            if f'{project.upper()}-{bug_id}' in pattern and 'fix' in commit_log.lower():
                status, matched_pattern = True, bug_id
                break

    return status, matched_pattern


def main_step_parse_diff_to_get_commit_bug_files_map(project, branch_name):
    """
    Obtaining [bug_fixing_commit_id,  bug id, changed files, commit log] file. OK
    :param project:
    :param branch_name:
    :return:
    """
    # result need to calculate [bug_fixing_commit_id,  bug id, changed files, commit log]
    commit_bug_files_map, content_of_prev_commit, last_commit_is_bug = [], [], False

    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    # Obtaining all bug id as matched patterns
    bug_id_list = get_bug_id_list(project)

    # Parsing diff.txt file line by line
    lines = read_data_from_file(rf'{analysis_file_path}/diff.txt')
    for line in lines:
        tmp = line.split("\t", 2)
        if len(tmp) != 1 and len(tmp) != 3:
            continue
        # When processing a new commit id line
        if len(tmp) != 3:
            # save the last commit info
            commit_bug_files_map.append(content_of_prev_commit) if last_commit_is_bug else None
            # Processing the current commit
            commit_id, commit_log = line[:40], line[40:]
            # Matching the bug patterns to decide whether the commit is a bug-fixing commit
            last_commit_is_bug, bug_id = match_bug_pattern(project, commit_log, bug_id_list)
            if not last_commit_is_bug:
                continue
            content_of_prev_commit = [commit_id, bug_id, [], commit_log]

        # When processing file change lines, add changed files into list
        if len(tmp) == 3 and last_commit_is_bug and tmp[2].endswith('.java'):
            content_of_prev_commit[2].append(tmp[2])  # tmp[2]: java files

    # save the last commit info
    commit_bug_files_map.append(content_of_prev_commit) if last_commit_is_bug else None

    # Output the result to file
    if not os.path.exists(f'{analysis_file_path}/BFC_commit_bug_files.pk'):
        dump_pk_result(f'{analysis_file_path}/BFC_commit_bug_files.pk', commit_bug_files_map)
        result = ''.join([f'{d[0]},{d[1]},{d[3]}' for d in commit_bug_files_map])
        save_data_to_file(f'{analysis_file_path}/BFC_commit_bug_log.csv', result)
    print('Output [bug-fixing commit, bug id, bug files, fix log] map file!')
    return commit_bug_files_map


def get_commit_bug_files_map(project, branch_name):
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    pk_data = load_pk_result(f'{analysis_file_path}/BFC_commit_bug_files.pk')
    # csv_data = read_data_from_file(f'{analysis_file_path}/commit_bug_log.csv')  # commit_bug_log_manually_checked.csv
    # # Select the commits id that have been identified by human beings
    # commit_ids = [line.split(',')[0] for line in csv_data]
    # pk_data = [c for c in pk_data if c[0] in commit_ids]
    return pk_data


def main_step_output_bug_fixing_commit_diff_file(project, branch_name):
    """
    Output bug-fixing commit diff file. OK.
    :return:
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    make_path(f'{analysis_file_path}/diff/')
    # Change current directory
    os.chdir(code_repos_paths[project])

    commit_bug_files_map = get_commit_bug_files_map(project, branch_name)

    for index in range(len(commit_bug_files_map)):
        commit_id = commit_bug_files_map[index][0]
        if not os.path.exists(f'{analysis_file_path}/diff/{commit_id}.txt'):
            # -p: show diff caused by bug fixing commit
            os.system(f'git log -p -n 1 --full-index {commit_id} > {analysis_file_path}/diff/{commit_id}.txt')
        print(f'Outputting {index}/{len(commit_bug_files_map)} diff file.') if index % 10 == 0 else None


def identify_bug_inducing_commit(project, branch_name, src_file, del_lines):
    """
    Leverage delete file lines in src file (i.e., buggy lines) to identifying bug-inducing commits. OK
    :param project:
    :param branch_name:
    :param src_file:
    :param del_lines:
    :return:
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'

    make_path(f'{analysis_file_path}/blame/')
    blame_file_path = f'{analysis_file_path}/blame/{src_file.replace("/", ".")}.txt'
    os.system(f'git blame --no-abbrev {src_file} > {blame_file_path}')
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


def main_step_parse_diff_file_to_get_bug_inducing_commit(project, branch_name):
    """
    Identifying defective file lines by tracking bug fixing commit. OK.
    :param project:
    :param branch_name:
    :return:
    """
    analysis_file_path = f'{analysis_file_paths[project]}/{branch_name}'
    # Change current directory
    os.chdir(code_repos_paths[project])

    result_text = 'bug_fixing_commit,src_files,bug_line_number_in_previous_commit,bug_inducing_commit\n'
    commit_bug_files_map = get_commit_bug_files_map(project, branch_name)
    for index in range(len(commit_bug_files_map)):
        bug_fixing_commit = commit_bug_files_map[index][0]  # bug fixing commit

        os.chdir(code_repos_paths[project])
        os.system(f'git reset --hard {bug_fixing_commit}~1')  # 定位到BIC的前一个commit(i.e., 包含bug的最后一个commit)

        bug_file_info = parse_diff(read_data_from_file(f'{analysis_file_path}/diff/{bug_fixing_commit}.txt'))
        # Processing the deleted lines in each changed file
        for bug_file in bug_file_info:
            bug_lines_delete = bug_file.hunk_infos['d']
            src_file = bug_file.src_file[2:]  # remove a/ to get the original file path
            # Skip if it is not a java file or there is no deleted lines
            if not src_file.endswith('.java') or len(bug_lines_delete) == 0:
                continue

            # the bug lines are introduced in their corresponding commits
            for instance in identify_bug_inducing_commit(project, branch_name, src_file, bug_lines_delete):
                line_in_previous_commit = str(instance[0])
                bug_inducing_commit = instance[1]
                result_text += f'{bug_fixing_commit},{src_file},{line_in_previous_commit},{bug_inducing_commit}\n'

    save_data_to_file(f'{analysis_file_path}/bug_commits_lines_info.csv', result_text)
    os.system(f'git reset --hard {commit_dict_index_hashcode[0]}')
