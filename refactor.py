# -*- coding: utf-8 -*-
from helper.file_helper import *
from helper.config import *


def generate_refactor_info(proj):
    ##### Refactoring line info
    refactor_list = []  # The list of refactor lines
    refactor_dict = {}  # The dict of [BFC commit -> refactor lines]

    lines = read_data_from_file(f'{data_collection_path}/Refactor/{proj}/refactor-{proj}.txt')
    cur_commit = ''
    # Iterating each lines in the file
    for line in lines:
        line = line.strip()
        if not line.endswith(')'):
            # Current line is a commit ID
            cur_commit = line
            refactor_dict[cur_commit] = [] if line not in refactor_dict else refactor_dict[cur_commit]
        else:
            # Current line is a refactor line information
            s = line.split('\t')[1].split(' at ')[-1][:-1]
            refactor_list.append(s) if s not in refactor_list else None
            refactor_dict[cur_commit].append(s) if s not in refactor_dict[cur_commit] else None

    # Save to file
    dump_pk_result(f'{data_collection_path}/Refactor/{proj}.pk', [refactor_list, refactor_dict])

    ##### Bug commits line info
    # The number of BFC lines
    bug_commits_line = set()
    path = f'{data_collection_path}/Analysis/{proj}/'
    a = 0
    for branch in os.listdir(path):
        if os.path.exists(f'{path}{branch}/bug_commits_lines_info.csv'):
            lines = read_data_from_file(f'{path}{branch}/bug_commits_lines_info.csv')[1:]
            a += len(lines)
            for line in lines:
                bug_commits_line.add(line)

    print(proj, len(refactor_list) / len(bug_commits_line))
    pass


if __name__ == '__main__':
    projects = [
        'ambari', 'amq', 'bookkeeper', 'calcite', 'cassandra', 'flink', 'groovy', 'hbase', 'hive', 'ignite',
        'log4j2', 'mahout', 'mng', 'nifi', 'nutch', 'storm', 'tika', 'ww', 'zookeeper',
    ]
    for project in projects:
        generate_refactor_info(project)
        # break
    pass
