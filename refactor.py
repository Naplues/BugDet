# -*- coding: utf-8 -*-
from helper.file_helper import *
from helper.config import *


def fun(proj):
    rt_path = f'D:/CLDP_data/DataCollection/'
    # The number of refactoring lines
    refactor_lines = []
    lines = read_data_from_file(f'{rt_path}Refactor/{proj}/refactor-{proj}.txt')
    for line in lines:
        if line.strip().endswith(')'):
            s = line.strip().split('\t')[1].split(' at ')[-1][:-1]
            refactor_lines.append(s) if s not in refactor_lines else None

    # The number of BFC lines
    path = f'{rt_path}/Analysis/{proj}/'
    BFC_lines_number = 0
    for branch in os.listdir(path):
        if os.path.exists(f'{path}{branch}/bug_commits_lines_info.csv'):
            lines = read_data_from_file(f'{path}{branch}/bug_commits_lines_info.csv')[1:]
            BFC_lines_number += len(lines)
            # for line in lines:
            #     BFC_lines.append(line) if line not in BFC_lines else None

    # print(len(refactor_lines), BFC_lines_number)
    print(len(refactor_lines) / BFC_lines_number)
    pass


if __name__ == '__main__':
    projects = [
        'ambari', 'amq', 'bookkeeper', 'calcite', 'cassandra', 'flink', 'groovy', 'hbase', 'hive', 'ignite',
        'log4j2', 'mahout', 'mng', 'nifi', 'nutch', 'storm', 'tika', 'ww', 'zookeeper',
    ]
    for project in projects:
        fun(project)
        # break
    pass
