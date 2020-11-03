# -*-coding:utf-8-*-
# The script has been tested successfully.
import logging

from unidiff import PatchSet, UnidiffParseError


class Diff(object):
    def __init__(self, src_file, tar_file, hunk_infos):
        """
        Initialize a diff instance OK.
        :param src_file: The file path in the previous code snapshot
        :param tar_file: The file path in the next code snapshot
        :param hunk_infos: The diff information, add lines number set and delete lines number set in tar_file
        """
        self.src_file = src_file
        self.tar_file = tar_file
        self.hunk_infos = hunk_infos

    def __str__(self):
        return f"{{Diff\n\tsrc_file: {self.src_file}\n\ttar_file: {self.tar_file}\n\thunk_infos: {self.hunk_infos}\n}}"

    def __repr__(self):
        return f"{{Diff\n\tsrc_file: {self.src_file}\n\ttar_file: {self.tar_file}\n\thunk_infos: {self.hunk_infos}\n}}"


def dump_one_hunk(hunk):
    """
    Algorithm 1 OK.
    Handling a single part in a patch.
    :param hunk: A changed part.
    :return: Temp result.
    """
    src_st_lineno = hunk.source_start
    tar_st_lineno = hunk.target_start
    d_cnt, a_cnt, del_linenos, add_linenos = 0, 0, [], []

    for line in hunk.source:
        if line.startswith('-'):
            del_linenos.append(src_st_lineno + d_cnt)
            d_cnt += 1
        else:
            d_cnt += 1
    for line in hunk.target:
        if line.startswith('+'):
            add_linenos.append(tar_st_lineno + a_cnt)
            a_cnt += 1
        else:
            a_cnt += 1
    del_linenos = sorted(del_linenos)
    add_linenos = sorted(add_linenos)
    return {"d": del_linenos, "a": add_linenos}


def dump_one_patch(patch):
    """
    Handling all changes in a patch (i.e., a changed file).  OK.
    :param patch: The changed informations of a changed file.
    :return: A Diff instance.
    """
    src_file = patch.source_file
    tar_file = patch.target_file
    del_linenos = []
    add_linenos = []
    for hunk in patch:
        hunk_info = dump_one_hunk(hunk)
        del_linenos.extend(hunk_info["d"])
        add_linenos.extend(hunk_info["a"])
    modify_info = {"d": del_linenos, "a": add_linenos}
    return Diff(src_file, tar_file, modify_info)


def parse_diff(diff_file):
    """
    Parse a diff file of one commit, and returen a Diff instance list.  OK.
    Patch: A diff file contains several patches, each of which describes the change informations of one changed file.
    Hunk：A Patch consists several hunks, all of which describe the different parts of change informations in the patch.
    :param diff_file: The file that contains diff information
    :return: A Diff instance list
    """
    diff_list = []
    try:
        patches = PatchSet(diff_file)
        diff_list = [dump_one_patch(patch) for patch in patches]
    except UnidiffParseError:
        logging.warning(f"Cannot analyze {diff_file}")
    return diff_list


def get_version_line(del_lines, add_lines, line):
    """
    calculate the line number in the target version
    :param del_lines:
    :param add_lines:
    :param line:
    :return:
    """
    source = 1
    target = 1
    line_map = dict()

    while source <= line:
        if source in del_lines:
            source += 1
            continue
        while target in add_lines:
            line_map[source] = -1  # 该行在source中不存在
            target += 1
        line_map[source] = target
        source += 1
        target += 1
    # print(line, "->", line_map[line])
    return line_map[line]


def get_version_line_2(del_lines, add_lines, line):
    # 目标版本删除了当前行,说明目标版本该行没有bug
    if line in del_lines:
        print("would never be executed!")
        return -1
    # 目标版本在当前行号之前被删除的行的数目
    t = line - len([x for x in del_lines if x < line])
    for x in add_lines:
        # 目标版本新加入的行在本行之前
        if x <= t:
            t += 1
    # print(line, "->", t)
    return t
