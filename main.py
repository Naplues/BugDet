# -*-coding:utf-8-*-
# The script has been tested successfully.


from steps.extract_bug_info import *
from steps.label_bug_version import *

if __name__ == '__main__':
    # Processing each project
    for proj in projects:
        # 1. Extracting the commit info (e.g., commit id, diff file)
        get_commit_info(proj)
        # 2. Mapping a bug report id to the bug_fixing_commit and the buggy files by parsing diff file of the repository
        parse_diff_to_commit_bug_files_map(proj)
        # 3. Manually remove non-bugs commit. commit_bug_log_manually_checked.csv TODO need review manually

        # 4. Outputting bug_fixing commit diff file
        output_bug_fixing_commit_diff_file(proj)
        # 5. Parsing the diff file to get the changed lines of a file, and then blame file to track bug inducing commit
        parse_diff_file_to_get_bug_inducing_commit(proj)
        # 6. Assigning the bugs for each version
        assign_bugs_for_each_version(proj)