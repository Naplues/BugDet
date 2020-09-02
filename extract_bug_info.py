# -*-coding:utf-8-*-
# The script has been tested successfully.

import os
import re
import time
import logging
from diff_helper import parse_diff

global project, branch_name, code_repository, root_path, result_root
global commit_dict_hashcode_index, commit_dict_index_hashcode


def output_commit_log():
    """
    OK.
    :return:None
    """
    if not os.path.exists(code_repository):
        os.makedirs(code_repository)
    if not os.path.exists(result_root):
        os.makedirs(result_root)

    # Change current directory
    os.chdir(code_repository)
    # Change branch
    # os.system("git checkout" + " " + branch_name)
    # Output different commit log information
    os.system("git log --pretty=format:\"%H %d\" > {}".format(os.path.join(result_root, "commit_ref.txt")))
    # os.system("git log --pretty=format:\"%H %ci\" > {}".format(os.path.join(result_root, "commit_time.txt")))
    # os.system("git log --pretty=format:\"%H %s\" > {}".format(os.path.join(result_root, "commit_subject.txt")))
    # os.system("git log --pretty=format:\"%H %an %ae\" > {}".format(os.path.join(result_root, "commit_author.txt")))
    time.sleep(1)


def get_commit_info():
    """
    OK.
    Get commit dict information.
    commit_dict_hashcode_index: Getting index from commit hash code
    commit_dict_index_hashcode: Getting hash code from commit index
    :return:
    """
    with open(os.path.join(result_root, "commit_ref.txt"), "r", encoding="utf-8") as fr:
        lines = fr.readlines()
    cnt = 0
    for line in lines:
        line = re.split("\s+", line.strip())
        commit_dict_hashcode_index[line[0]] = cnt
        commit_dict_index_hashcode[cnt] = line[0]
        cnt += 1


def get_file_change_informations():
    """
    OK.
    Tracking the informations (including the number of add lines and delete lines) of all files that are modified by
    each commit.
    :return:None
    """
    # Change current directory
    os.chdir(code_repository)
    os.system("git config diff.renameLimit 3999")
    # --diff-filter=M 意味着只抽取 Modified 的文件, 不考虑Added Deleted等情况
    os.system("git log --pretty=oneline --diff-filter=M --numstat > {}".format(os.path.join(result_root, "diff.txt")))
    os.system("git config --unset diff.renameLimit")


def get_all_bug_ids():
    """
    OK.
    Read Bug ID. ACCUMULO-3
    :return:
    """
    bug_pattern_path = root_path + "/BugReport/statistics/" + project + ".csv"
    with open(bug_pattern_path, "r", encoding="utf-8", errors="ignore") as fr:
        data = fr.readlines()
    for i in range(len(data)):
        data[i] = data[i].strip().split(',')[1]
    return data


def check_bug_exist(text, pattern):
    """
    OK.
    :param text:
    :param pattern:
    :return:
    """
    text = text.upper()
    m = re.search(project.upper() + r"-\d+", text)
    if not m:
        return False, ""
    else:
        m = m.group()
        if m in pattern:
            return True, m
        else:
            return False, ""


# OK 获取commit 和 bug 对应表
def git_bug_commit():
    """
    Match a bug id, its bug files, and its bug-fixing commit
    :return:
    """
    with open(os.path.join(result_root, "diff.txt"), "r", encoding="utf-8") as fr:
        lines = fr.readlines()
    # [commit_id,  bug id, changed files]
    data = list()
    # 每个commit对应的记录
    t_line = list()
    is_bug = False

    pattern = get_all_bug_ids()  # 获取所有bug id作为待匹配模式

    # 逐行解析处理diff.txt文件
    for line in lines:
        tmp = line.split("\t", 2)
        if len(tmp) != 1 and len(tmp) != 3:
            continue
        # 新的 commit 日志行
        if len(tmp) != 3:
            # 保存上一个commit信息,对第一条记录直接跳过
            if is_bug:
                data.append(t_line)

            commit_id = line[:40]
            commit_log = line[40:]
            # 检查该日志中是否含有bug修复信息
            is_bug, bug_id = check_bug_exist(commit_log, pattern)
            if not is_bug:
                continue
            t_line = [commit_id, bug_id, list()]

        # 文件change 行: 只添加包含bug的commit中的java文件
        if len(tmp) == 3 and is_bug:  # and tmp[2].endswith('.java'):  TODO
            t_line[2].append(tmp[2])

    # 判断最后一个commit信息
    if is_bug:
        data.append(t_line)

    with open(os.path.join(result_root, "commit_bugId.csv"), "w", encoding="utf-8", errors="ignore") as fr:
        for d in data:
            fr.write(d[0] + "," + d[1] + "\n")
    return data


def output_bug_fixing_commit_diff(data):
    """
    OK.
    Output bug-fixing commit diff file.
    :param data:
    :return:
    """
    if not os.path.exists(result_root + "diff/"):
        os.mkdir(result_root + "diff/")
    for item in data:
        commit_id = item[0]
        output_file = commit_id + ".txt"  # --full-index TODO 是否需要忽略空白行-B
        os.system(
            "git log -p -n 1 --full-index {} > {}".format(commit_id, os.path.join(result_root, "diff/" + output_file)))


def get_bug_inducing_commit(src_file, del_lines):
    """
    Leverage delete file lines in src file (i.e., buggy lines) to tracking bug-inducing commits
    :param src_file:
    :param del_lines:
    :return:
    """
    os.system("git blame --abbrev=7 {} > {}".format(src_file, os.path.join(result_root, "temp.txt")))
    with open(os.path.join(result_root, "temp.txt"), encoding="utf-8", errors="ignore") as fr:
        res = fr.readlines()
    ans = list()
    for line in del_lines:
        if line > len(res):
            logging.warning("git blame line error! " + src_file + ":" + str(line))
            continue
        # 遇到空白行跳过
        if res[line - 1].strip().endswith(")"):
            continue
        # 被删除的那一行
        tmps = re.split("\s+", res[line - 1].strip())

        if len(tmps) > 0:
            ans.append([line, tmps[0]])  # [行号, line_inducing_commit_id]
    os.remove(os.path.join(result_root, "temp.txt"))
    return ans


def resolve_diff_file(data):
    """
    OK.
    # 定位有缺陷的file lines, tracking bug fixing commit.
    :param data:
    :return:
    """
    fw = open(os.path.join(result_root, "bug_commits_lines_info.csv"), 'w', encoding="utf-8")
    os.chdir(code_repository)

    for item in data:
        bug_fixing_commit_id = item[0]  # bug fixing commit

        os.chdir(code_repository)
        os.system("git reset --hard {}~1".format(bug_fixing_commit_id))  # 定位到修复前一个commit(i.e., 包含bug的最后一个commit)
        time.sleep(0.01)
        diff = open(result_root + "diff/" + bug_fixing_commit_id + ".txt", 'r', encoding='UTF-8')
        try:
            bug_file_info = parse_diff(diff)
        except:
            logging.warning("Cannot analyze diff " + result_root + "diff/" + bug_fixing_commit_id + ".txt")
            continue

        # 处理每个变化的文件中的删除行
        for bug_file in bug_file_info:
            bug_lines_delete = bug_file.hunk_infos['d']
            src_file = bug_file.src_file[2:]  # 去除a/
            # 没有删除行或者变化文件不是Java文件
            if len(bug_lines_delete) == 0 or not src_file.endswith('.java'):
                continue

            result = get_bug_inducing_commit(src_file, bug_lines_delete)
            # the bug lines are introduced in their corresponding commits
            for res in result:
                bug_line_in_previous_commit = str(res[0])
                bug_line_inducing_commit_id = res[1]
                fw.write(bug_fixing_commit_id + ","
                         + src_file + ","
                         + bug_line_in_previous_commit + ","
                         + bug_line_inducing_commit_id + "\n")
    fw.close()
    os.system("git reset --hard {}".format(commit_dict_index_hashcode[0]))


if __name__ == '__main__':
    #
    projects = ["ambari", "amq", "avro", 'calcite', "camel", "curator", "flink", "flume", "geode", "groovy", "hudi",
                "ignite", "kafka", "kylin", "lang", "mahout", "netbeans", "mng", "nifi", "nutch", "rocketmq", "shiro",
                "storm", "tika", "ww", "zeppelin", "zookeeper",
                ]
    for proj in projects:
        # 项目信息
        project = proj
        branch_name = "master"
        root_path = "F:/BugDetection"
        commit_dict_hashcode_index = dict()
        commit_dict_index_hashcode = dict()

        code_repository = root_path + "/Repository/" + project + "/"
        result_root = root_path + "/Result/bug/" + project + "/" + branch_name + "/"

        output_commit_log()
        get_commit_info()
        get_file_change_informations()
        data = git_bug_commit()
        output_bug_fixing_commit_diff(data)
        resolve_diff_file(data)
