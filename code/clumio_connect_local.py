# Copyright 2024, Clumio Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import requests
from datetime import datetime, timedelta, timezone
import boto3
import time
import json
import random
import string
from botocore.exceptions import ClientError
import re
import urllib.parse

api_dict = {
    "008": {"name": "Connections",
            "api": "connections/aws/connection-groups",
            "header": "application/api.clumio.aws-environments=v1+json",
            "version": "v1",
            "desc": "Add AWS Connections",
            "type": "post",
            "success": 200,
            "query_parms": {
                "limit": 100,
                "start": 1,
                "filter": {
                    "account_native_id": [
                        "$eq",
                        "$begins_with"],
                    "master_region": ["$eq"],
                    "aws_region": ["$eq"],
                    "asset_types_enabled": ["ebs", "rds", "DynamoDB", "EC2MSSQL", "S3", "ec2"],
                    "description": ["$eq"]
                }
            }
            }
}


class API:
    def __init__(self, id):
        self.id = id
        self.good = True
        self.name = api_dict.get(id, {}).get('api', None)
        self.version = api_dict.get(id, {}).get('version', None)
        self.type = api_dict.get(id, {}).get('type', None)
        self.pagnation = False
        self.debug = 0
        if api_dict.get(id, {}).get('success', None):
            self.success = api_dict.get(id, {}).get('success', None)
        else:
            if self.debug > 7: print(
                f"API init debug new APIs {id},  success {api_dict.get(id, {}).get('success', None)}")
            self.good = False

        self.url_prefix = "https://us-west-2.api.clumio.com/"
        self.header = {}
        self.payload = {}
        self.payload_flag = False
        self.body_parms_flag = False
        self.body_parms = {}
        self.token_flag = False
        self.token = None
        self.good = True
        self.type_get = False
        self.type_post = False
        self.current_count = 0
        self.total_count = 0
        self.total_pages_count = 0
        self.error_msg = None
        self.exec_error_flag = False
        self.aws_account_id = "080005437757"
        self.aws_account_id_flag = False
        self.aws_region = "us-east-1"
        self.aws_region_flag = False
        self.region_option = ["us-east-1", "us-west-2", "us-east-2", "us-west-1"]
        self.aws_tag_key = ""
        self.aws_tag_value = ""
        self.aws_tag_flag = False
        self.usage_type = "S3"
        self.aws_credentials = None
        self.aws_connect_good = False
        self.dump_to_file_flag = False
        self.dump_file_name = None
        self.dump_bucket = None
        self.aws_bucket_region = None
        self.file_iam_role = None
        self.import_bucket = None
        self.aws_import_bucket_region = None
        self.import_file_name = None
        self.import_file_flag = False
        self.import_data = {}
        self.type_post = False
        self.task_id = None
        self.task_id_flag = False
        self.pagination = False
        # #print("Hello world its me Dave")
        # Function to Create an AWS Session using IAM role

        if api_dict.get(id, {}).get('header', None):
            self.accept_api = api_dict.get(id, {}).get('header', None)
        else:
            if self.debug > 7: print(
                f"API init debug new APIs {id},  header {api_dict.get(id, {}).get('header', None)}")
            self.good = False
        # #print(f"DICT {api_dict.get(id, {}).get('type', None)}")
        if api_dict.get(id, {}).get('type', None):
            type = api_dict.get(id, {}).get('type', None)
            if type == 'get':
                self.type_get = True
                # #print("found get")
            elif type == 'post':
                self.type_post = True
            else:
                if self.debug > 7: print(
                    f"API init debug new APIs {id},  type {api_dict.get(id, {}).get('type', None)}")
                self.good = False
        else:
            if self.debug > 7: print(
                f"API init debug new APIs {id},  type {api_dict.get(id, {}).get('type', None)}")
            self.good = False
        if api_dict.get(id, {}).get('api', None):
            self.url = self.url_prefix + api_dict.get(id, {}).get('api', None)
            self.url_full = self.url
        else:
            self.good = False
        if api_dict.get(id, {}).get('body_parms', False):
            self.body_parms_flag = True
            self.body_parms = api_dict.get(id, {}).get('body_parms', {})
        else:
            self.payload_flag = False
            self.payload = {}
        if api_dict.get(id, {}).get('query_parms', False):
            self.query_parms_flag = True
            self.query_parms = api_dict.get(id, {}).get('query_parms', {})
        else:
            self.query_parms_flag = False
            self.query_parms = {}
        if api_dict.get(id, {}).get('body_parms', False):
            self.body_parms_flag = True
            self.body_parms = api_dict.get(id, {}).get('body_parms', {})
        else:
            self.body_parms_flag = False
            self.body_parms = {}
        if api_dict.get(id, {}).get('pathParms', False):
            self.pathParms_flag = True
            self.pathParms = api_dict.get(id, {}).get('query_parms', {})
        else:
            self.pathParms_flag = False
            self.pathParms = {}

    # Set debug Level
    def set_debug(self, value):
        try:
            self.debug = int(value)
            return True
        except ValueError:
            return False

    def get_task_id(self):
        if self.task_id_flag:
            return self.task_id
        else:
            return False

    def get_error(self):
        return self.error_msg

    def get_version(self):
        # #print(self.version,type(self.version))
        ##print("hi")
        return self.version

    def set_token(self, token):
        self.token = token
        self.token_flag = True
        bear = f"Bearer {self.token}"

        if self.good:
            if self.type_get:
                self.header = {"accept": self.accept_api, "authorization": bear}
            elif self.type_post:
                self.header = {"accept": self.accept_api, "content-type": "application/json", "authorization": bear}
            return self.header

    def set_url(self, suffix):
        # #print(f"hi in set {prefix}")
        if self.good:
            self.url_full = self.url + suffix
            # #print(self.url_full)

    def get_url(self):
        if self.good:
            return self.url_full
        else:
            return False

    def set_pagination(self):
        self.pagination = True

    def get_header(self):
        if self.good:
            return self.header
        else:
            return False

    def set_bad(self):
        self.good = False

    def set_get(self):

        self.type_get = True

    def set_post(self):

        self.type_post = True

    def exec_api(self):
        if self.debug > 7: print(f"exec_api: In Post {self.id},  type post {self.type_post} type get {self.type_get}")
        if self.type_get:

            if self.good and self.token_flag:

                url = self.get_url()
                header = self.get_header()
                if self.debug > 0: print(f"exec_api - url {url}")
                if self.debug > 0: print(f"exec_api - header {header}")

                try:
                    response = requests.get(url, headers=header)
                except ClientError as e:
                    ERROR = e.response['Error']['Code']
                    status_msg = "failed to initiate session"
                    if self.debug > 3: print("exec_api failed in request")
                    return {"status": status_msg, "msg": ERROR}
                status = response.status_code

                response_text = response.text
                if self.debug > 1: print(f"exec_api - get request response {response_text}")
                response_dict = json.loads(response_text)

                if not status == self.success:
                    status_msg = f"API status {status}"
                    ERROR = response_dict.get('errors')
                    self.exec_error_flag = True
                    self.error_msg = f"status: {status_msg}, msg: {ERROR}"
                    if self.debug > 3: print(f"exec_api get request error resonse - {self.error_msg}")
                    self.good = False
                if self.pagination:
                    self.current_count = response_dict.get("current_count")
                    self.total_count = response_dict.get("total_count")
                    self.total_pages_count = response_dict.get("total_pages_count")
                    if self.debug > 1: print(
                        f"exec_api - pagination info current, total, total pages {self.current_count} {self.total_count} {self.total_pages_count}")
                return response_dict
        elif self.type_post:
            if self.debug > 7: print(f"exec_api: post Post  {id},  header {api_dict.get(id, {}).get('header', None)}")
            if self.good and self.token_flag and self.payload_flag:
                if self.debug > 7: print(f"exec_api: In Post {id},  header {api_dict.get(id, {}).get('header', None)}")
                url = self.get_url()
                header = self.get_header()
                payload = self.get_payload()
                if self.debug > 0: print(f"exec_api - url {url}")
                if self.debug > 0: print(f"exec_api - header {header}")
                if self.debug > 0: print(f"exec_api - payload {payload}")
                try:
                    response = requests.post(url, json=payload, headers=header)
                    if self.debug > 1: print(f"exec_api - response {response}")
                except ClientError as e:
                    ERROR = e.response['Error']['Code']
                    status_msg = "failed to initiate session"
                    if self.debug > 3: print(f"exec_api post request failed - {self.error_msg}")
                    return {"status": status_msg, "msg": ERROR}
                status = response.status_code

                response_text = response.text
                if self.debug > 1: print(f"exec_api - request response {response_text}")
                response_dict = json.loads(response_text)
                self.task_id = response_dict.get("task_id", None)
                print(f"resposne {response_dict} task id {self.task_id}")
                if self.task_id:
                    self.task_id_flag = True
                else:
                    self.task_id_flag = False

                if not status == self.success:
                    status_msg = f"API status {status}"
                    ERROR = response_dict.get('errors')
                    self.exec_error_flag = True
                    self.error_msg = f"status: {status_msg}, msg: {ERROR}"
                    self.good = False
                    if self.debug > 3: print(f"exec_api post request response - {self.error_msg}")
                return response_dict
        else:
            self.good = False
            return False

    def get_payload(self):
        if self.payload_flag:
            return self.payload


class ClumioConnectAccount(API):
    def __init__(self):
        super(ClumioConnectAccount, self).__init__("008")
        self.rnd_string = ''.join(random.choices(string.ascii_letters, k=5))
        self.id = "008"
        self.aws_account_to_connect = None
        self.master_aws_region = None
        self.master_aws_account_id = None
        self.aws_region_list_to_connect = []
        self.asset_types_to_enable = []
        self.aws_account_list_to_connect_flag = False
        self.master_aws_region_flag = False
        self.master_aws_account_id_flag = False
        self.aws_region_list_to_connect_flag = False
        self.asset_types_to_enable_flag = False
        self.good = True

        if api_dict.get(self.id, {}).get('type', None):
            # print(f"api_dict 01")
            if self.good:
                # print(f"api_dict 02")
                if api_dict.get(self.id, {}).get('type', None) == "get":
                    # print(f"api_dict 03")
                    self.set_get()
                elif api_dict.get(self.id, {}).get('type', None) == "post":
                    # print(f"api_dict 04")
                    self.set_post()
                else:
                    # print(f"api_dict 05")
                    self.set_bad()

    def confirm_payload(self):
        if self.aws_account_list_to_connect_flag and self.master_aws_account_id_flag and self.master_aws_region_flag and self.aws_region_list_to_connect_flag and self.asset_types_to_enable_flag:
            self.payload_flag = True
            self.payload = {
                "account_native_id": self.aws_account_to_connect,
                "master_region": self.master_aws_region,
                "master_aws_account_id": self.master_aws_account_id,
                "aws_regions": self.aws_region_list_to_connect,
                "asset_types_enabled": self.asset_types_to_enable,
                "template_permission_set": "all"
            }
        else:
            self.payload_flag = False
        return self.payload_flag

    def set_account(self, account_id):
        self.aws_account_to_connect = account_id
        self.master_aws_account_id = account_id
        self.aws_account_list_to_connect_flag = True
        self.master_aws_account_id_flag = True
        self.confirm_payload()

    def set_regions(self, region_list):
        self.master_aws_region = region_list[0]
        self.aws_region_list_to_connect = region_list
        self.master_aws_region_flag = True
        self.aws_region_list_to_connect_flag = True
        self.confirm_payload()

    def set_aws_services(self, service_list):
        self.asset_types_to_enable = service_list
        self.asset_types_to_enable_flag = True
        self.confirm_payload()

    def run(self):
        if self.payload_flag:
            result = self.exec_api()
            # print(result)
            return result
        else:
            raise Exception("Payload not set to run connect API")

    def run_clumio_deploy_stack_local(self, current_aws_session, region, url, token, id):
        print(f"in deploy clumio stack")
        deployment_template_url = url
        clumio_token = token
        external_id = id
        if current_aws_session == "boto3":
            cft_client = boto3.client('cloudformation')
        else:
            cft_client = current_aws_session.client('cloudformation')

        try:
            deploy_rsp = cft_client.create_stack(
                StackName=f'clumiodeploy-{self.rnd_string}',
                TemplateURL=deployment_template_url,
                Parameters=[
                    {
                        'ParameterKey': 'ClumioToken',
                        'ParameterValue': clumio_token
                    },
                    {
                        'ParameterKey': 'RoleExternalId',
                        'ParameterValue': external_id
                    },
                    {
                        'ParameterKey': 'PermissionModel',
                        'ParameterValue': 'SELF_MANAGED'
                    },
                    {
                        'ParameterKey': 'PermissionsBoundaryARN',
                        'ParameterValue': ''
                    },
                ],
                Capabilities=[
                    'CAPABILITY_NAMED_IAM'
                ],
                DisableRollback=True,
                TimeoutInMinutes=60,
            )
            print(f"deploy_status: {deploy_rsp}")
        except ClientError as e:
            error = e.response['Error']['Code']
            error_msg = f"failed to deploy stack {error}"
            if self.debug > 5: print(f"error: {error_msg}")
            return False, error_msg
        return True, ""