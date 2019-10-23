# sample_utils.py Code Sample
#
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import sys
import os
import json
import time
import resource_uri_utils
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.netapp import AzureNetAppFilesManagementClient
from datetime import datetime
from msrestazure.azure_exceptions import CloudError


def get_credentials():
    credential_file = os.environ.get('AZURE_AUTH_LOCATION')

    with open(credential_file) as credential_file_contents:
        credential_info = json.load(credential_file_contents)

    subscription_id = credential_info['subscriptionId']

    credentials = ServicePrincipalCredentials(
        client_id=credential_info['clientId'],
        secret=credential_info['clientSecret'],
        tenant=credential_info['tenantId']
    )
    return credentials, subscription_id


def console_output(message):
    print('{}: {}'.format(datetime.now(), message))


def get_bytes_in_tib(size):
    return size / 1024 / 1024 / 1024 / 1024


def get_tib_in_bytes(size):
    return size * 1024 * 1024 * 1024 * 1024


def wait_for_no_anf_resource(client, resourceId, intervalInSec=10, retries=60):
    for i in range(0, retries):
        time.sleep(intervalInSec)
        try:
            if resource_uri_utils.is_anf_snapshot(resourceId):
                client.snapshots.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId),
                    resource_uri_utils.get_anf_capacity_pool(resourceId),
                    resource_uri_utils.get_anf_volume(resourceId),
                    resource_uri_utils.get_anf_snapshot(resourceId)
                )
            elif resource_uri_utils.is_anf_volume(resourceId):
                client.volumes.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId),
                    resource_uri_utils.get_anf_capacity_pool(resourceId),
                    resource_uri_utils.get_anf_volume(resourceId)
                )
            elif resource_uri_utils.is_anf_capacity_pool(resourceId):
                client.pools.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId),
                    resource_uri_utils.get_anf_capacity_pool(resourceId)
                )
            elif resource_uri_utils.is_anf_account(resourceId):
                client.accounts.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId)
                )
        except CloudError as ex:
            break


def wait_for_anf_resource(client, resourceId, intervalInSec=10, retries=60):
    for i in range(0, retries):
        time.sleep(intervalInSec)
        try:
            if resource_uri_utils.is_anf_snapshot(resourceId):
                client.snapshots.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId),
                    resource_uri_utils.get_anf_capacity_pool(resourceId),
                    resource_uri_utils.get_anf_volume(resourceId),
                    resource_uri_utils.get_anf_snapshot(resourceId)
                )
                break
            elif resource_uri_utils.is_anf_volume(resourceId):
                client.volumes.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId),
                    resource_uri_utils.get_anf_capacity_pool(resourceId),
                    resource_uri_utils.get_anf_volume(resourceId)
                )
                break
            elif resource_uri_utils.is_anf_capacity_pool(resourceId):
                client.pools.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId),
                    resource_uri_utils.get_anf_capacity_pool(resourceId)
                )
                break
            elif resource_uri_utils.is_anf_account(resourceId):
                client.accounts.get(
                    resource_uri_utils.get_resource_group(resourceId),
                    resource_uri_utils.get_anf_account(resourceId)
                )
                break
        except CloudError as ex:
            pass
