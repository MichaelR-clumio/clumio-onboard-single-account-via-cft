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

# FOR EXAMPLE PURPOSES ONLY

#
# Requirements: 
#  Local account to be onboarded
#  Role in local account that can run deployment
#  S3 bucket - needs to be in same region where lambda will run
# Copy zip file to S3 bucket.  Keeps bucket name and object name to enter as parameters in the CF.

# Upload lambda zip file "clumio_connect_local.zip" into S3 bucket

# Run the lambda deployment CFT, clumio_onboard_single_account-cft.yaml
#
# Other CFT parameters to set:
# Need to select region(s) and resource(s)
