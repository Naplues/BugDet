# -*- coding: utf-8 -*-
from helper.file_helper import *

p1 = rf'D:\CLDP_data\DataCollection\Analysis\ambari\AMBARI-24152-branch-2.6\bug_commits_lines_info.csv'
p2 = rf'D:\CLDP_data1\DataCollection\Analysis\ambari\AMBARI-24152-branch-2.6\bug_commits_lines_info.csv'

d1 = read_data_from_file(p1)[1:]
d2 = read_data_from_file(p2)[1:]

print(len(d1), len(d2))
d1_set = set(d1)
d2_set = set(d2)

print(d1_set-d2_set)
