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
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.netapp import azure_net_app_files_management_client
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


def wait_for_no_account(client, resource_group_name, anf_account_name):
    co=0
    while co<5:
        time.sleep(10)
        co += 1
        try:
            client.accounts.get(resource_group_name, anf_account_name)
            console_output('\t\t{} - Account {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
        except CloudError as ex:
            console_output('\t\t{} - Account {} not found, exting wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
            break


def wait_for_account(client, resource_group_name, anf_account_name):
    co=0
    while co<5:
        time.sleep(10)
        co += 1
        try:
            client.accounts.get(resource_group_name, anf_account_name)
            console_output('\t\t{} - Account {} found, exiting wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
            break
        except CloudError as ex:
            console_output('\t\t{} - Account {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
            pass


def wait_for_pool(client, resource_group_name, anf_account_name, capacitypool_name):
    co=0
    while co<10:
        time.sleep(10)
        co += 1
        try:
            client.pools.get(resource_group_name, anf_account_name, capacitypool_name)
            console_output('\t\t{} - Capacity Pool {} found, exiting wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
            break
        except CloudError as ex:
            console_output('\t\t{} - Capacity Pool {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
            pass


def wait_for_no_pool(client, resource_group_name, anf_account_name, capacitypool_name):
    co=0
    while co<10:
        time.sleep(10)
        co += 1
        try:
            client.pools.get(resource_group_name, anf_account_name, capacitypool_name)
            console_output('\t\t{} - Capacity Pool {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
        except CloudError as ex:
            console_output('\t\t{} - Capacity Pool {} not found, exiting wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
            break


def wait_for_volume(client, resource_group_name, anf_account_name, capacitypool_name, volume_name):
    co=0
    while co<10:
        time.sleep(20)
        co += 1
        try:
            client.volumes.get(resource_group_name, anf_account_name, capacitypool_name, volume_name)
            console_output('\t\t{} - Volume {} found, exiting wait...'.format(sys._getframe().f_code.co_name, volume_name))
            break
        except CloudError as ex:
            console_output('\t\t{} - Volume {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, volume_name))
            pass


def wait_for_no_volume(client, resource_group_name, anf_account_name, capacitypool_name, volume_name):
    co=0
    while co<10:
        time.sleep(20)
        co += 1
        try:
            client.volumes.get(resource_group_name, anf_account_name, capacitypool_name, volume_name)
            console_output('\t\t{} - Volume {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, volume_name))
        except CloudError as ex:
            console_output('\t\t{} - Volume {} not found, exiting wait...'.format(sys._getframe().f_code.co_name, volume_name))
            break


def wait_for_snapshot(client, resource_group_name, anf_account_name, capacitypool_name, volume_name, snapshot_name):
    co=0
    while co<10:
        time.sleep(10)
        co += 1
        try:
            client.snapshots.get(resource_group_name, anf_account_name, capacitypool_name, volume_name, snapshot_name)
            console_output('\t\t{} - Snapshot {} found, exiting wait...'.format(sys._getframe().f_code.co_name, snapshot_name))
            break
        except CloudError as ex:
            console_output('\t\t{} - Snapshot {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, snapshot_name))
            pass


def wait_for_no_snapshot(client, resource_group_name, anf_account_name, capacitypool_name, volume_name, snapshot_name):
    co=0
    while co<10:
        time.sleep(10)
        co += 1
        try:
            client.snapshots.get(resource_group_name, anf_account_name, capacitypool_name, volume_name, snapshot_name)
            console_output('\t\t{} - Snapshot {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, snapshot_name))
        except CloudError as ex:
            console_output('\t\t{} - Snapshot {} not found, exiting wait...'.format(sys._getframe().f_code.co_name, snapshot_name))
            break