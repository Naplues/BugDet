# -*-coding:utf-8-*-
# The script has been tested successfully.

import os
import pickle

root_path = r'D:/CLDP_data'

# ww:struts amq:activemq mvn:maven lang:commons-lang
# "ambari", "amq", "avro", 'calcite', "camel", "curator", "flink", "flume", "geode", "groovy", "hudi", "ignite",
# "kafka", "kylin", "lang", "mahout", "netbeans", "mng", "nifi", "nutch", "rocketmq", "shiro","storm", "tika", "ww",
# "zeppelin", "zookeeper",
# projects = ["mnemonic"]
projects = ['groovy']


def make_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_data_to_file(path, data):
    with open(path, 'w', encoding='utf-8') as fw:
        fw.write(data)


def read_data_from_file(path):
    with open(path, 'r', encoding='utf-8', errors="ignore") as fr:
        lines = fr.readlines()
    return lines


def dump_pk_result(path, data):
    with open(path, 'wb') as file:
        pickle.dump(data, file)


def load_pk_result(path):
    with open(path, 'rb') as file:
        data = pickle.load(file)
    return data


if __name__ == '__main__':
    a = [1, 2, 3, 4, 5]
