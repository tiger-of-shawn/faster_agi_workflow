from nodes.BaseGraphNode import BaseGraphNode
import os
import json
import threading
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import nls

class AliyunTTS(BaseGraphNode):
    def __init__(self, name : str = '', **kwargs):
        self.access_key_id = kwargs.get('access_key_id', os.getenv("ACCESS_KEY_ID"))
        self.access_secret = kwargs.get('access_secret', os.getenv("ACCESS_SECRET"))
        self.app_key = kwargs.get('app_key', os.getenv("APP_KEY"))


    def get_token(self):
        client = AcsClient(self.access_key, self.access_secret, "cn-shanghai")
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')

        try:
            response = client.do_action_with_exception(request)
            response_json = json.loads(response)
            if 'Token' in response_json and 'Id' in response_json['Token']:
                token = response_json['Token']['Id']
                # print("获取的 Token:", token)
                return token
        except Exception as e:
            print("获取 Token 失败:", e)
            return None
