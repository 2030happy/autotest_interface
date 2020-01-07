# -*- coding:utf-8 -*-
"""
封装HTTP请求操作
1.http_request是主方法，直接提供外部调用
2.__http_get、--http_post是实际底层分类调用的方法
"""

import requests, os, logging
from autotest_interface.common import opmysql
from autotest_interface.public import config

class RequestInterface(object):
    # 定义处理不同类型的请求参数，包含字典、字符串、空值
    def __new_param(self,param):
        try:
            # 如果接口请求参数是一个字符串类型的字典，则用eval函数将其还原成字典形式
            if isinstance(param,str) and param.startswith('{'):
                new_param=eval(param)
            # 如果参数是None，直接返回一个空字符串
            elif param==None:
                new_param=''
            # 其他情况返回本来的参数
            else:
                new_param=param
        except Exception as error: #记录日志到log.txt文件
            new_param=''
            logging.basicConfig(filename = config.src_path + '/log/sysyerror.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(error)
        return new_param


    # POST请求，参数在body中。__http_post是一个私有方法，只能在该类中调用，不能在类的外部使用。
    def __http_post(self,interface_url,headerdata,interface_param):
        """
        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :return: 字典形式结果
        """
        try:
            if interface_url !='':
                temp_interface_param = self.__new_param(interface_param)
                response = requests.post(url=interface_url,
        headers=headerdata,data=temp_interface_param,verify=False,timeout=10)
                if response.status_code == 200:
                    durtime = (response.elapsed.microseconds)/1000 # 发起请求
                    # 和响应到达的时间，单位ms
                    result = {'code':'0000', 'message':'成功', 'data':response.text}
                else:
                    result={'code':'2004','message':'接口返回状态错误','data':[]}
            elif interface_url == '':
                result={'code':'2002','message':'接口地址参数为空','data':[]}
            else:
                result={'code':'2003','message':'接口地址错误','data':[]}
        except Exception as error:  #记录日志到log.txt文件
            result={'code':'9999','message':'系统异常','data':[]}
            logging.basicConfig(
                filename=config.src_path + '/log/sysyerror.log',
                level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(error)
        return result


    # GET请求，参数在接口地址后面
    def __http_get(self,interface_url,headerdata,interface_param):
        """
        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :return: 字典形式结果
        """
        try:
            if interface_url != '':
                temp_interface_param=self.__new_param(interface_param)
                if interface_url.endswith('?'):
                    requrl = interface_url + temp_interface_param
                else:
                    requrl = interface_url + '?' + temp_interface_param
                response = requests.get(url=requrl, headers=headerdata,
                                        verify=False,timeout=10)
                # print response
                if response.status_code==200:
                    durtime = (response.elapsed.microseconds) / 1000 #发起请求和响应到达的时间，单位ms
                    result = {'code':'0000', 'message':'成功','data':response.text}
                else:
                    result={'code':'3004','message':'接口返回状态错误','data':[]}
            elif interface_url == '':
                result={'code':'3002','message':'接口地址参数为空','data':[]}
            else:
                result={'code':'3003','message':'接口地址错误','data':[]}
        except Exception as error:#记录日志到log.txt文件
            result={'code':'9999','message':'系统异常','data':[]}
            logging.basicConfig(filename=config.src_path + '/log/syserror.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(error)
        return result


    # 统一处理HTTP请求
    def http_request(self,interface_url,headerdata,interface_param,request_type):
        """
        :param interface_url: 接口地址
        :param headerdata: 请求头文件
        :param interface_param: 接口请求参数
        :param requet_type: 请求类型
        :return: 字典形式结果
        """
        try:
            if request_type == 'get' or request_type=='GET':
                result = self.__http_get(interface_url,headerdata,interface_param)
            elif request_type=='post' or request_type=='POST':
                result = self.__http_post(interface_url,headerdata,interface_param)
            else:
                result = {'code':'1000','message':'请求类型错误','data':request_type}
        except Exception as error:#记录日志到log.txt文件
            result = {'code': '9999', 'message': '系统异常', 'data': []}
            logging.basicConfig(
                filename=config.src_path + '/log/sysyerror.log',
                level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(error)
        return result


if __name__ == "__main__":
    test_interface = RequestInterface() #实例化HTTP请求类

    # 实例化MySQL处理类
    test_db = opmysql.OperationDbInterface(host_db='localhost', user_db='root',
            passwd_db='2030',name_db='you', port_db=3306, link_type=0)
    sen_sql = "select exe_mode,url_interface,header_interface, " \
              "params_interface from case_interface where name_interface='GetServerStatus'"
    params_interface=test_db.select_one(sen_sql)
    print(params_interface)
    if params_interface['code'] == '0000':
        url_interface = params_interface['data']['url_interface']
        temp = params_interface['data']['header_interface']
        headerdata=eval(params_interface['data']['header_interface']) #将unicode转换成字典
        param_interface = params_interface['data']['params_interface']
        type_interface = params_interface['data']['exe_mode']
        # print(type_interface)

        if url_interface != '' and headerdata != '' and param_interface != '' and type_interface !='':
            result=test_interface.http_request(interface_url=url_interface,
                        headerdata=headerdata,interface_param=param_interface,
                                               requet_type=type_interface)
            if result['code'] == '0000':
                result_resp = result['data']
                test_db.op_sql("updata case_interface set result_interface='%s'"
                               "where id=1" %result_resp) #将结果更新到case_interface
                print("处理HTTP请求成功，返回数据是： %s" %result_resp)
            else:
                print("出来HTTP请求失败")
    else:
        print("获取接口测试用例数据失败")



