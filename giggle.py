#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = '40kuai'

"""
1. 检测ncdu命令。根据系统进行安装。
2. 使用ncdu命令生成相关文件信息文件。
3. 对文件进行处理。
"""

import os
import sys
import json
import subprocess


class InstallError(Exception):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return self.message


class PerformCmd(object):
    def __init__(self,cmd=None):
        self.cmd = cmd

    def run(self,cmd):
        ret = subprocess.Popen(cmd, shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
        err = ret.stderr.read()
        if err:
            raise Exception(err)
        else:
            return True


class InstallNcdu(object):
    """检测ncdu命令。根据系统进行安装。"""
    def __init__(self):
        self.system_name = sys.platform
        self.install_stutus = False
        if self.system_name == 'linux2':
            ret_status = PerformCmd('yum -y install ncdu')
            if ret_status:
                self.install_stutus = True


class FilterFile(object):
    """通过处理文件，按照给定大小筛选大文件"""

    def __init__(self, check_dir='/', file_path='/tmp/', file_name='ncdu.json'):
        install_ncdu = InstallNcdu()
        if not install_ncdu.install_stutus:
            raise InstallError('install ncdu error')
        self.files_list = []
        self.files_info_list = []
        self.check_dir = check_dir
        self.file_path = file_path
        self.file_name = file_name
        self.all_string = None
        self.create_file_status = self.create_file()

    def create_file(self):
        """ncdu创建文件"""
        ncdu_file_path = os.path.join(self.file_path, self.file_name)
        create_file_cmd = 'ncdu %s -o %s%s' % (self.check_dir, self.file_path, self.file_name)
        ret_id = PerformCmd(create_file_cmd)
        if ret_id:
            with open(ncdu_file_path, ) as file:
                self.all_string = json.load(file)[3]
            return True
        else:
            return False

    def print_size(self, list_obj, size=104857600):
        """输出文件大小大于 104857600"""
        if isinstance(list_obj, list):
            for i in list_obj:
                self.files_list.append(list_obj[0]['name'])
                self.print_size(i)
                self.files_list.pop()
        else:
            if isinstance(list_obj, dict) and 'asize' in list_obj:
                if list_obj['asize'] > size:
                    print "file path: %s, file size: %.2fM" % (
                        os.path.join('/'.join(self.files_list)[1:],list_obj['name']),
                        list_obj['asize']/1024/1024
                    )

    def print_top(self, list_obj, top=5):
        pass

    def print_f(self, file_type, num):
        print_obj = getattr(self, 'print_%s' % file_type)
        print_obj(self.all_string, num)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        file_type,num = sys.argv[1:]
        if file_type in ["top", "size"] and num.isdigit():
            obj = FilterFile()
            obj.print_f(file_type=file_type, num=int(num))
            exit(0)
    print 'usage: python giggle top|size num'

