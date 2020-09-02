# -*-coding:utf-8-*-

import os


projects = ["accumulo", "activemq", "any23", "camel", "flink", "gora", "ivy", "kafka", "kylin", "lens", "mnemonic", "nutch", "storm", "struts", "tika", "zeppelin", "zookeeper"]
projects = ["mnemonic"]

for project in projects:
	code_release_path = "F:/BugDetection/Project/Releases/" + project + "/"
	# 切换到Releases目录下
	os.chdir(code_release_path)
	# 处理Release下所有文件夹
	for file in os.listdir(code_release_path):
		if file.find(".zip") > 0 or file.find(".udb") > 0:
			continue
		print(file)
		os.system("und create -db {}.udb -languages java".format(file))
		os.system("und -db {}.udb add {}".format(file, code_release_path + file))
		os.system("und -db {} -quiet analyze".format(file))
