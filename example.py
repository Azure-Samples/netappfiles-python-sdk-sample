import os
import json
import time
import sys
import resource_uri_utils
import azure.mgmt.netapp.models
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.netapp import azure_net_app_files_management_client
from azure.mgmt.netapp.models import NetAppAccount, CapacityPool, Volume, Snapshot
from datetime import datetime
from azure.common import AzureException

LOCATION = 'eastus'
RESOURCE_GROUP_NAME = 'anf01-rg'
VNET_NAME = 'pmc-vnet-01'
SUBNET_NAME = 'anf-sn'
VNET_RESOURCE_GROUP_NAME = 'anf01-rg'
ANF_ACCOUNT_NAME = Haikunator().haikunate(delimiter='')
CAPACITYPOOL_NAME = "Pool01"
CAPACITYPOOL_SERVICE_LEVEL = "Standard"
CAPACITYPOOL_SIZE = 4398046511104 # 4TiB
VOLUME_NAME = 'Vol-{}-{}'.format(ANF_ACCOUNT_NAME, CAPACITYPOOL_NAME)
VOLUME_USAGE_QUOTA = 107374182400 # 100GiB
SNAPSHOT_NAME = 'Snapshot-{}'.format(VOLUME_NAME)
VOLUME_FROM_SNAPSHOT_NAME = 'Vol-{}'.format(SNAPSHOT_NAME)


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


def create_account(client, resource_group_name, anf_account_name, location, tags=None, active_directories=None):
    account_body = NetAppAccount(
        location=location,
        tags=tags)

    client.accounts.create_or_update(account_body, resource_group_name, anf_account_name).wait()


def create_capacitypool(client, resource_group_name, anf_account_name, capacitypool_name, service_level, size, location, tags=None):
    capacitypool_body = CapacityPool(
        location=location,
        service_level=service_level,
        size=size)

    client.pools.create_or_update(capacitypool_body, resource_group_name, anf_account_name, capacitypool_name).wait()
    

def create_volume(client, resource_group_name,  anf_account_name, capacitypool_name, volume_name, volume_usage_quota, service_level, subnet_id, location, tags=None):
    volume_body = Volume(
        usage_threshold = volume_usage_quota,
        creation_token = volume_name,
        location = location,
        service_level = service_level,
        subnet_id = subnet_id)

    client.volumes.create_or_update(volume_body, resource_group_name, anf_account_name, capacitypool_name, volume_name).wait()
    

def wait_for_no_account(client, resource_group_name, anf_account_name):
    co=0
    while co<5:
        co += 1
        try:
            client.accounts.get(resource_group_name, anf_account_name)
            console_output('\t\t{} - Account {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
        except AzureException as ex:
            console_output('\t\t{} - Account {} not found, exting wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
            break
        
        time.sleep(2)


def wait_for_account(client, resource_group_name, anf_account_name):
    co=0
    while co<5:
        co += 1
        try:
            client.accounts.get(resource_group_name, anf_account_name)
            console_output('\t\t{} - Account {} found, exiting wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
            break
        except AzureException as ex:
            console_output('\t\t{} - Account {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, anf_account_name))
            pass

        time.sleep(2)


def wait_for_pool(client, resource_group_name, anf_account_name, capacitypool_name):
    co=0
    while co<10:
        co += 1
        try:
            client.pools.get(resource_group_name, anf_account_name, capacitypool_name)
            console_output('\t\t{} - Capacity Pool {} found, exiting wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
            break
        except AzureException as ex:
            console_output('\t\t{} - Capacity Pool {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
            pass

        time.sleep(10)


def wait_for_no_pool(client, resource_group_name, anf_account_name, capacitypool_name):
 
    co=0
    while co<10:
        co += 1
        try:
            client.pools.get(resource_group_name, anf_account_name, capacitypool_name)
            console_output('\t\t{} - Capacity Pool {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
        except AzureException as ex:
            console_output('\t\t{} - Capacity Pool {} not found, exiting wait...'.format(sys._getframe().f_code.co_name, capacitypool_name))
            break

        time.sleep(10)


def wait_for_volume(client, resource_group_name, anf_account_name, capacitypool_name, volume_name):
    co=0
    while co<10:
        co += 1
        try:
            client.volumes.get(resource_group_name, anf_account_name, capacitypool_name, volume_name)
            console_output('\t\t{} - Volume {} found, exiting wait...'.format(sys._getframe().f_code.co_name, volume_name))
            break
        except AzureException as ex:
            console_output('\t\t{} - Volume {} not found, retrying wait...'.format(sys._getframe().f_code.co_name, volume_name))
            pass
        
        time.sleep(10)


def wait_for_no_volume(client, resource_group_name, anf_account_name, capacitypool_name, volume_name):
    co=0
    while co<10:
        co += 1
        try:
            client.volumes.get(resource_group_name, anf_account_name, capacitypool_name, volume_name)
            console_output('\t\t{} - Volume {} still found, retrying wait...'.format(sys._getframe().f_code.co_name, volume_name))
        except AzureException as ex:
            console_output('\t\t{} - Volume {} not found, exiting wait...'.format(sys._getframe().f_code.co_name, volume_name))
            break

        time.sleep(20)


def run_example():
    """Azure NetApp Files management example."""

    print("Azure NetAppFiles Python SDK Sample - Sample project that performs CRUD management operations with Azure NetApp Files SDK with Python")
    print("-------------------------------------------------------------------------------------------------------------------------------------")

    #
    # Creating the Azure NetApp Files Client with an Application (service principal) token provider
    #
    credentials, subscription_id = get_credentials()
    anf_client = azure_net_app_files_management_client.AzureNetAppFilesManagementClient(credentials, subscription_id)

    #
    # Creating an Azure NetApp Account
    #
    console_output('Creating Azure NetApp Files account ...')
    account = None
    try:
        create_account(anf_client, RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME, LOCATION)
        wait_for_account(anf_client, RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME)
        account = anf_client.accounts.get(RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME)
        console_output('\tAccount successfully created, resource id: {}'.format(account.id))
    except AzureException as ex:
        console_output('An error ocurred. Error details: {}'.format(ae))

    #
    # Creating a Capacity Pool
    #
    console_output('Creating Capacity Pool ...')
    capacity_pool = None
    try:
        create_capacitypool(anf_client, RESOURCE_GROUP_NAME, account.name, CAPACITYPOOL_NAME,  CAPACITYPOOL_SERVICE_LEVEL, CAPACITYPOOL_SIZE, LOCATION)
        wait_for_pool(anf_client, RESOURCE_GROUP_NAME, account.name, CAPACITYPOOL_NAME)
        capacity_pool = anf_client.pools.get(RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME, CAPACITYPOOL_NAME)
        console_output('\tCapacity Pool successfully created, resource id: {}'.format(capacity_pool.id))
    except AzureException as ex:
        console_output('An error ocurred. Error details: {}'.format(ae))

    #
    # Creating a Volume
    #
    console_output('Creating a Volume ...')
    subnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(subscription_id, VNET_RESOURCE_GROUP_NAME, VNET_NAME, SUBNET_NAME)
    volume = None
    try:
        pool_name = resource_uri_utils.get_anf_capacitypool(capacity_pool.id)

        create_volume(anf_client, RESOURCE_GROUP_NAME, account.name, pool_name, VOLUME_NAME, VOLUME_USAGE_QUOTA, CAPACITYPOOL_SERVICE_LEVEL, subnet_id, LOCATION)
        wait_for_volume(anf_client, RESOURCE_GROUP_NAME, account.name, pool_name, VOLUME_NAME)
        volume = anf_client.volumes.get(RESOURCE_GROUP_NAME, account.name, pool_name, VOLUME_NAME)
        console_output('\tVolume successfully created, resource id: {}'.format(volume.id))
    except AzureException as ex:
        console_output('An error ocurred. Error details: {}'.format(ae))



   


# This script expects that the following environment vars are set:
#
# AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret
# AZURE_SUBSCRIPTION_ID: with your Azure Subscription Id
#

if __name__ == "__main__":
    run_example()
