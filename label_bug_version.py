# -*-coding:utf-8-*-

import os
import re
import logging
from helper.file_helper import parse_diff, get_version_line

global project, branch_name

commit_version_dict = dict()
commit_dict_hashcode_index = {}
commit_all = []


def read_version():
    """
    OK.
    :return:
    """
    with open(version_root, 'r', encoding='utf-8') as fr:
        lines = fr.readlines()
    for line in lines:
        if line.strip():
            line = line.strip()
            spices = line.split(",")
            if spices[0] == branch_name:
                commit_id = spices[2][:8]
                commit_version_name = spices[1]
                commit_version_dict[commit_id] = commit_version_name


def get_commit_info():
    """
    OK.
    """
    with open(os.path.join(result_root, "commit_ref.txt"), "r", encoding="utf-8") as fr:
        lines = fr.readlines()
    cnt = 0
    for line in lines:
        line = re.split("\s+", line.strip())
        commit_dict_hashcode_index[line[0][:8]] = cnt
        commit_all.append(line[0][:8])
        cnt += 1


def get_commit_version():
    """
    Algorithm 2
    :return:
    """
    with open(os.path.join(result_root, "bug_commits_lines_info.csv"), "r", encoding="utf-8") as fr:
        lines = fr.readlines()
    os.chdir(code_repository)
    result = ["target version, bug line in target version, bug line in last commit, "
              "bug-inducing commit, bug-fixing commit, bug file path"
              ]
    cmd_temp = ""

    # 待测版本的commit id and version name
    for version_commit, version_name in commit_version_dict.items():
        print(version_name)
        for strline in lines:
            strline = strline.strip()
            # [commit_id, bug_file, bug_line, inducing commit]
            temp = strline.split(",")
            bug_line_fixing_commit_id = temp[0][:8]
            bug_file_path = temp[1]
            bug_line_in_previous_commit = temp[2]
            bug_line_inducing_commit = temp[3]

            if bug_line_inducing_commit.startswith("^"):
                for c in commit_all:
                    if bug_line_inducing_commit == ("^" + c[0:7]):
                        bug_line_inducing_commit = c
                        break

            if bug_line_inducing_commit not in commit_dict_hashcode_index.keys():
                logging.warning("Can not find the commit_id: " + bug_line_inducing_commit)
                continue

            # 9 [8] 7 [6] 5 4 [3] 2 1
            # 当前版本的commit在 引入bug的commit和修复bug的commit之间 after commitStart and before commit_id 之间的时期为bug生存期
            # print(len(commit_dict_hashcode_index))
            if version_commit not in commit_dict_hashcode_index.keys():
                continue
            version_index = commit_dict_hashcode_index[version_commit]
            bug_inducing_index = commit_dict_hashcode_index[bug_line_inducing_commit]
            bug_fixing_index = commit_dict_hashcode_index[bug_line_fixing_commit_id]
            if bug_inducing_index >= version_index > bug_fixing_index:
                # 查看bug commit和指定版本k之间的diff
                # the bug lines in Vm must can be founded in Vt
                cmd = "git diff {}~1 {} -- {} > {}".format(
                    bug_line_fixing_commit_id, version_commit, bug_file_path,
                    os.path.join(result_root, "diff_temp.txt"))
                if cmd_temp != cmd:
                    cmd_temp = cmd
                    os.system(cmd_temp)

                diff = open(os.path.join(result_root, "diff_temp.txt"), 'r', encoding="utf-8")

                # We need to relocate the target lines when temp diff file is not empty.
                if os.path.getsize(os.path.join(result_root, "diff_temp.txt")):
                    try:
                        version_diff = parse_diff(diff)

                        # 当解析前后的版本中文件路径发生变更时，暂不考虑
                        if version_diff[0].tar_file == "/dev/null":
                            continue
                        del_lines = version_diff[0].hunk_infos['d']
                        add_lines = version_diff[0].hunk_infos['a']
                        version_line = get_version_line(del_lines, add_lines, int(bug_line_in_previous_commit))

                    except:
                        logging.warning("Cannot analyze diff")
                        continue
                # There is no change between the target version and the last bug-containing commmit
                # when temp diff file is empty. Thus, directly assign.
                else:
                    version_line = bug_line_in_previous_commit

                result.append(""
                              + version_name + ","
                              + str(version_line) + ", "
                              + bug_line_in_previous_commit + ","
                              + bug_line_inducing_commit + ","
                              + bug_line_fixing_commit_id + ","
                              + bug_file_path + ","
                              )
                diff.close()
    # bug在指定版本的文件及行号
    with open(os.path.join(result_root, "result.csv"), "w", encoding="utf-8") as fr:
        for line in result:
            fr.write(line + "\n")


if __name__ == '__main__':

    projects = ["ambari", "amq", "avro", 'calcite', "camel", "curator", "flink", "flume", "geode", "groovy", "hudi",
                "ignite", "kafka", "kylin", "lang", "mahout", "netbeans", "mng", "nifi", "nutch", "rocketmq", "shiro",
                "storm", "tika", "ww", "zeppelin", "zookeeper",
                ]

    root_path = "F:/BugDetection"
    for proj in projects:
        project = proj
        branch_name = "master"
        code_repository = root_path + "/Repository/" + project + "/"
        result_root = root_path + "/Result/bug/" + project + "/" + branch_name + "/"
        version_root = root_path + "/Version/" + project + ".csv"

        read_version()
        get_commit_info()
        get_commit_version()
