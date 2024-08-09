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


import boto3
import time
from botocore.exceptions import ClientError
from clumio_connect_local import ClumioConnectAccount


def lambda_handler(events, context):

    bear = events.get('bear',None)
    debug = events.get('debug',0)
    account_id = events.get('aws_account_id',None)
    region_list = events.get('aws_region_list',None)
    aws_service_list = events.get('aws_service_list',None)
    master_region = events.get('master_region',None)
    if not master_region == region_list[0]:
        return {"status": 403, "msg": f"not running in region that is first in region list {master_region} {region_list}"}
    if debug > 5: print(f"connect_lambda: {account_id} {region_list} {aws_service_list}")
    if not (bear and account_id and region_list and aws_service_list):
        return {"status":401,"msg": f"missing input {bear} {account_id} {region_list} {aws_service_list}"}

    clumio_connect_api = ClumioConnectAccount()
    clumio_connect_api.set_token(bear)
    clumio_connect_api.set_debug(debug)
    clumio_connect_api.set_account(account_id)
    clumio_connect_api.set_regions(region_list)
    clumio_connect_api.set_aws_services(aws_service_list)
    rsp = clumio_connect_api.run()
    if debug > 5: print(rsp)
    deployment_template_url_clumio = rsp.get("deployment_template_url", None)
    clumio_token = rsp.get("id", None)
    external_id = rsp.get("external_id", None)
    if not (deployment_template_url_clumio and clumio_token and external_id):
        return {"status": 401, "msg": f"clumio connect issue {rsp}","regions": [], "services": []}

    time.sleep(5)
    # Deploy CFT stack to connect AWS account to Clumio
    [status, msg] = clumio_connect_api.run_clumio_deploy_stack_local("boto3", region_list[0], deployment_template_url_clumio, clumio_token, external_id)

    if status:
        return {"status": 200, "msg": "stack deploy started", "regions": region_list, "services": aws_service_list}
    else:
        return {"status": 402, "msg": msg, "regions": [], "services": []}
