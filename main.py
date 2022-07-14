# -*-coding:utf-8-*-
# The script has been tested successfully.

from extract_bug_info import *
from label_bug_version import *

analysis_file_path = gl.get_value('analysis_file_path')


def preprocessing_step(project, branch_names):
    for branch_name in branch_names:
        analysis_path = f'{analysis_file_paths[project]}/{branch_name}'
        # make folders
        make_path(analysis_path)
        # output commit log info and code diff info
        export_commit_info(branch_name, analysis_path)
        export_diff_info(branch_name, analysis_path)

    # load commit -> branch list directory c_to_branches
    load_commit_branch_dict(project, branch_names)
    print('=' * 20 + f' Export commit information for each available branch of {project.upper()}.' + '=' * 20)


def main_steps_for_each_branch(project, branch_names):
    for branch_index in range(len(branch_names)):
        branch_name = branch_names[branch_index]
        print('=' * 20 + f' Processing {branch_index + 1}/{len(branch_names)} branch {branch_name} ' + '=' * 20)
        os.system(rf'git checkout -f {branch_name}')
        # the path of analysis data
        analysis_path = f'{analysis_file_paths[project]}/{branch_name}'
        # 1. Extracting the commit info (e.g., commit id, diff file)
        load_commit_info(analysis_path)  # OK
        # 2. Mapping a bug report id to the bug_fixing_commit and the buggy files by parsing diff file of the repository
        main_step_parse_diff_to_get_commit_bug_files_map(project, analysis_path)
        # 3. Outputting bug_fixing commit diff file
        main_step_export_bug_fixing_commit_diff_file(analysis_path)
        # 4. Parsing the diff file to get the changed lines of a file, and then blame file to track bug inducing commit
        main_step_parse_diff_file_to_get_bug_inducing_commit(analysis_path)
        # 5. Assigning the bugs for each version
        main_step_assign_bugs_for_each_version(project, branch_name, analysis_path)


def collect_dataset():
    # Processing each project
    for proj in projects:
        # 1. Collecting the bug information from JIRA
        # collect_bugs(proj)
        # Change current directory to Root/Repository/ambari/
        os.chdir(code_repos_paths[proj])
        # 2. branch information
        # branches = load_selected_branches(proj)
        # prepare steps before extracting info
        # preprocessing_step(proj, branches)
        # main steps to extract bug info
        # main_steps_for_each_branch(proj, branches)
        # combine bug info from all branches
        combine_bug_info_from_all_branch(proj)
        # combine_tmp_bug_info_from_all_branch(proj)
        # Link bug id and buggy files and buggy lines
        # link_bug_with_files_and_lines(proj)


if __name__ == '__main__':
    collect_dataset()
    pass
