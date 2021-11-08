# -*-coding:utf-8-*-
# The script has been tested successfully.

from extract_bug_info import *
from label_bug_version import *


def prepare_step(branch_names):
    for branch_name in branch_names:
        # make folders
        make_path(analysis_file_path[branch_name])
        # output commit log info
        output_commit_info(branch_name, analysis_file_path[branch_name])
    # load commit -> branch list directory c_to_branches
    load_commit_branch_dict(proj)
    print('Prepare step finish!')


def main_steps_for_each_branch(project, branch_names):
    for branch_name in branch_names:
        print(f'Processing branch {branch_name}')
        # the path of analysis data
        analysis_path = analysis_file_path[branch_name]
        # 1. Extracting the commit info (e.g., commit id, diff file)
        get_commit_info(branch_name, analysis_path)  # OK
        # 2. Mapping a bug report id to the bug_fixing_commit and the buggy files by parsing diff file of the repository
        main_step_parse_diff_to_get_commit_bug_files_map(project, analysis_path)
        # 3. Outputting bug_fixing commit diff file
        main_step_output_bug_fixing_commit_diff_file(analysis_path)
        # 4. Parsing the diff file to get the changed lines of a file, and then blame file to track bug inducing commit
        main_step_parse_diff_file_to_get_bug_inducing_commit(analysis_path)
        # 5. Assigning the bugs for each version
        main_step_assign_bugs_for_each_version(project, branch_name, analysis_path)


if __name__ == '__main__':
    # Processing each project
    for proj in projects:
        # 1. Collecting the bug information from JIRA
        # collect_bugs(proj)
        # Change current directory
        os.chdir(code_repos_paths[proj])
        # 2. branch information
        branches = selected_branches(proj)
        # The path of analysis files
        analysis_file_path = dict(zip(branches, [f'{analysis_file_paths[proj]}/{branch}' for branch in branches]))
        # prepare steps before extracting info
        prepare_step(branches)
        # main steps to extract bug info
        main_steps_for_each_branch(proj, branches)
        # Link bug id and buggy files and buggy lines
        link_bug_with_files_and_lines(proj)
