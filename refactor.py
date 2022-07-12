# -*- coding: utf-8 -*-
from helper.file_helper import *
from helper.config import *


def fun(proj):
    # The number of refactoring lines
    path = f'D:/CLDP_data/DataCollection/Refactor/{proj}/refactor-{proj}.txt'
    refactor_lines = []
    lines = read_data_from_file(path)
    for line in lines:
        if line.strip().endswith(')'):
            s = line.strip().split('\t')[1].split(' at ')[-1][:-1]
            refactor_lines.append(s) if s not in refactor_lines else None

    # The number of BFC lines
    path = f'D:/CLDP_data/DataCollection/Analysis/{proj}/'
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
        'ambari',  # ok
        'amq',  # ok activemq
        'bookkeeper',
        'calcite',  # ok
        'cassandra',  # ok
        'flink',
        'groovy',  # ok
        'hbase',
        'hive',  # ok
        'ignite',  # ok
        'log4j2',  # logging-log4j2
        'mahout',  # ok
        'mng',  # maven
        'nifi',
        'nutch',
        'storm',
        'tika',
        'ww',  # struts
        'zookeeper',  # ok
    ]
    for project in projects:
        fun(project)
        # break
    pass
