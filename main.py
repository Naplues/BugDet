# -*-coding:utf-8-*-
# The script has been tested successfully.

from steps.collect_bug_report import *
from steps.extract_bug_info import *
from steps.label_bug_version import *


def main(project, branch_name):
    # 3. Extracting the commit info (e.g., commit id, diff file)
    # get_commit_info(project, branch_name)
    # 4. Mapping a bug report id to the bug_fixing_commit and the buggy files by parsing diff file of the repository
    # main_step_parse_diff_to_get_commit_bug_files_map(project, branch_name)

    # 5. Outputting bug_fixing commit diff file
    # main_step_output_bug_fixing_commit_diff_file(project, branch_name)
    # 6. Parsing the diff file to get the changed lines of a file, and then blame file to track bug inducing commit
    # main_step_parse_diff_file_to_get_bug_inducing_commit(project, branch_name)
    # 7. Assigning the bugs for each version
    # main_step_assign_bugs_for_each_version(project, branch_name)
    pass


if __name__ == '__main__':
    # Processing each project
    for proj in projects:
        # 1. Collecting the bug information from JIRA
        # collect_bugs(proj)
        # 2. branch information
        branch_names = output_branch_info(proj)
        for branch in branch_names:
            main(proj, branch)
        combine_bug_info_from_all_branch(proj)
