import os
import json
import azure.mgmt.netapp.models
from haikunator import Haikunator
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.netapp import azure_net_app_files_management_client
from azure.mgmt.netapp.models import NetAppAccount, CapacityPool, Volume, Snapshot, ExportPolicyRule
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


def create_account(client, resource_group_name, anf_account_name=ANF_ACCOUNT_NAME, location=LOCATION, tags=None, active_directories=None):
    account_body = NetAppAccount(location=location, tags=tags)
    client.accounts.create_or_update(account_body, resource_group_name, anf_account_name).wait()


def create_capacitypool(client, resource_group_name, capacitypool_name=CAPACITYPOOL_NAME, service_level=CAPACITYPOOL_SERVICE_LEVEL, size=CAPACITYPOOL_SIZE, anf_account_name=ANF_ACCOUNT_NAME,  location=LOCATION, tags=None, active_directories=None):
    capacitypool_body = CapacityPool(location=location, service_level=service_level, size=size)
    return client.pools.create_or_update(capacitypool_body, resource_group_name, anf_account_name, capacitypool_name).wait()
    

def run_example():
    """Azure NetApp Files management example."""

    print("Azure NetAppFiles Python SDK Sample - Sample project that performs CRUD management operations with Azure NetApp Files SDK with Python")
    print("-------------------------------------------------------------------------------------------------------------------------------------")

    #
    # Create the Azure NetApp Files Client with an Application (service principal) token provider
    #
    credentials, subscription_id = get_credentials()
    anf_client = azure_net_app_files_management_client.AzureNetAppFilesManagementClient(credentials, subscription_id)

    #
    # Creates an Azure NetApp Account
    #
    console_output('Creating Azure NetApp Files account ...')
    account = None
    try:
        create_account(anf_client, RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME, LOCATION)
        account = anf_client.accounts.get(RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME)
        console_output('\tAccount successfully created, resource id: {}'.format(account.id))
    except Exception as ae:
        console_output('An error ocurred. Error details: {}'.format(ae))

    #
    # Creates a Capacity Pool
    #
    console_output('Creating Capacity Pool ...')
    capacity_pool = None
    try:
        create_capacitypool(anf_client, RESOURCE_GROUP_NAME, CAPACITYPOOL_NAME,  CAPACITYPOOL_SERVICE_LEVEL, CAPACITYPOOL_SIZE, account.name, LOCATION)
        capacity_pool = anf_client.pools.get(RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME, CAPACITYPOOL_NAME)
        console_output('\tCapacity Pool successfully created, resource id: {}'.format(capacity_pool.id))
    except Exception as ae:
        console_output('An error ocurred. Error details: {}'.format(ae))

    #subnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(subscription_id, VNET_RESOURCE_GROUP_NAME, VNET_NAME, SUBNET_NAME)


# This script expects that the following environment vars are set:
#
# AZURE_TENANT_ID: with your Azure Active Directory tenant id or domain
# AZURE_CLIENT_ID: with your Azure Active Directory Application Client ID
# AZURE_CLIENT_SECRET: with your Azure Active Directory Application Secret
# AZURE_SUBSCRIPTION_ID: with your Azure Subscription Id
#

if __name__ == "__main__":
    run_example()
