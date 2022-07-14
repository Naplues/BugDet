# -*- coding: utf-8 -*-

import helper.global_variable as gl

projects = [
    'ambari',  # ok
    'amq',  # ok activemq
    'bookkeeper',
    'calcite', # ok
    'cassandra', # ok
    'flink',
    'groovy',  # ok
    'hbase',
    'hive', # ok
    'ignite', # ok
    'log4j2', # logging-log4j2
    'mahout', # ok
    'mng',  # maven
    'nifi',
    'nutch',
    'storm',
    'tika',
    'ww', # struts
    'zookeeper',  # ok
]
# 所有文件的根目录
root_path = r'D:/CLDP_data'
# D:/CLDP_data
code_repos_paths = dict(zip(projects, [f'D:/CLDP_data/Repository/{proj}' for proj in projects]))

data_collection_path = f'{root_path}/DataCollection'
# Root/DataCollection/Data/ambari
dataset_paths = dict(zip(projects, [f'{data_collection_path}/Data/{proj}' for proj in projects]))
# Root/DataCollection/Analysis/ambari
analysis_file_paths = dict(zip(projects, [f'{data_collection_path}/Analysis/{proj}' for proj in projects]))
# Root/DataCollection/Version/ambari.csv
version_file_paths = dict(zip(projects, [f'{data_collection_path}/Version/{proj}.csv' for proj in projects]))

bug_report_path = f'{data_collection_path}/BugReport/reports'

gl.init()
gl.set_value('code_repos_paths', code_repos_paths)
gl.set_value('dataset_paths', dataset_paths)
gl.set_value('analysis_file_paths', analysis_file_paths)
gl.set_value('version_file_paths', version_file_paths)
