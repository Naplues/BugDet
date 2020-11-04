# -*-coding:utf-8-*-
# The script has been tested successfully.

from extract_bug_info import *
from label_bug_version import *


def main_steps_for_each_branch(project, branch_name, analysis_path):
    # 3. Extracting the commit info (e.g., commit id, diff file)
    get_commit_info(branch_name, analysis_path)  # OK
    # 4. Mapping a bug report id to the bug_fixing_commit and the buggy files by parsing diff file of the repository
    main_step_parse_diff_to_get_commit_bug_files_map(project, analysis_path)
    # 5. Outputting bug_fixing commit diff file
    main_step_output_bug_fixing_commit_diff_file(analysis_path)
    # 6. Parsing the diff file to get the changed lines of a file, and then blame file to track bug inducing commit
    main_step_parse_diff_file_to_get_bug_inducing_commit(analysis_path)
    # 7. Assigning the bugs for each version
    main_step_assign_bugs_for_each_version(project, branch_name, analysis_path)
    pass


if __name__ == '__main__':
    # Processing each project
    for proj in projects:

        # 1. Collecting the bug information from JIRA
        # collect_bugs(proj)
        # Change current directory
        os.chdir(code_repos_paths[proj])
        # 2. branch information

        for branch in selected_branches(proj):
            # the path of analysis data
            analysis_file_path = f'{analysis_file_paths[proj]}/{branch}'
            make_path(analysis_file_path)

            main_steps_for_each_branch(proj, branch, analysis_file_path)

        # combine_bug_info_from_all_branch(proj)
