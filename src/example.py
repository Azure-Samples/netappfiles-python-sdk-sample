# example.py Code Sample
#
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import time
import sample_utils
import resource_uri_utils
import azure.mgmt.netapp.models
from haikunator import Haikunator
from azure.core.exceptions import AzureError
from azure.identity import ClientSecretCredential
from azure.mgmt.netapp import NetAppManagementClient
from azure.mgmt.netapp.models import NetAppAccount, \
    CapacityPool, \
    Volume, \
    Snapshot, \
    CapacityPoolPatch, \
    ExportPolicyRule, \
    VolumePatchPropertiesExportPolicy, \
    VolumePatch
from azure.mgmt.resource import ResourceManagementClient
from sample_utils import console_output, print_header, resource_exists

# Variables to be changed to be in accordance to the environment where this sample will be executed
SHOULD_CLEANUP = False
LOCATION = 'eastus2'
RESOURCE_GROUP_NAME = 'anf01-rg'
VNET_NAME = 'vnet-02'
SUBNET_NAME = 'anf-sn'
VNET_RESOURCE_GROUP_NAME = 'anf01-rg'
ANF_ACCOUNT_NAME = Haikunator().haikunate(delimiter='')
CAPACITYPOOL_NAME = "Pool01"
CAPACITYPOOL_SERVICE_LEVEL = "Standard"
CAPACITYPOOL_SIZE = 4398046511104  # 4TiB
VOLUME_NAME = 'Vol-{}-{}'.format(ANF_ACCOUNT_NAME, CAPACITYPOOL_NAME)
VOLUME_USAGE_QUOTA = 107374182400  # 100GiB
SNAPSHOT_NAME = 'Snapshot-{}'.format(VOLUME_NAME)
VOLUME_FROM_SNAPSHOT_NAME = 'Vol-{}'.format(SNAPSHOT_NAME)

# Resource SDK related (change only if API version is not supported anymore)
VIRTUAL_NETWORKS_SUBNET_API_VERSION = '2018-11-01'

def create_account(client, resource_group_name, anf_account_name,
                   location, tags=None):
    """Creates an Azure NetApp Files Account

    Function that creates an Azure NetApp Account, which requires building the
    account body object first.

    Args:
        client (NetAppManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            account will be created
        location (string): Azure short name of the region where resource will
            be deployed
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        NetAppAccount: Returns the newly created NetAppAccount resource
    """

    account_body = NetAppAccount(location=location, tags=tags)

    return client.accounts.begin_create_or_update(resource_group_name,
                                            anf_account_name,
                                            account_body).result()


def create_capacitypool_async(client, resource_group_name,
                              anf_account_name, capacitypool_name,
                              service_level, size, location, tags=None):
    """Creates a capacity pool within an account

    Function that creates a Capacity Pool, capacity pools are needed to define
    maximum service level and capacity.

    Args:
        client (NetAppManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            capacity pool will be created, it needs to be the same as the
            Account
        anf_account_name (string): Name of the Azure NetApp Files Account where
            the capacity pool will be created
        capacitypool_name (string): Capacity pool name
        service_level (string): Desired service level for this new capacity
            pool, valid values are "Ultra","Premium","Standard"
        size (long): Capacity pool size, values range from 4398046511104
            (4TiB) to 549755813888000 (500TiB)
        location (string): Azure short name of the region where resource will
            be deployed, needs to be the same as the account
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        CapacityPool: Returns the newly created capacity pool resource
    """

    capacitypool_body = CapacityPool(
        location=location,
        service_level=service_level,
        size=size,
        tags=tags)

    return client.pools.begin_create_or_update(resource_group_name, 
                                               anf_account_name,  
                                               capacitypool_name,
                                               capacitypool_body).result()


def create_volume(client, resource_group_name, anf_account_name,
                  capacitypool_name, volume_name, volume_usage_quota,
                  service_level, subnet_id, location, tags=None):
    """Creates a volume within a capacity pool

    Function that in this example creates a NFSv3 volume within a capacity
    pool, as a note service level needs to be the same as the capacity pool.
    This function also defines the volume body as the configuration settings
    of the new volume.

    Args:
        client (NetAppManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            volume will be created, it needs to be the same as the account
        anf_account_name (string): Name of the Azure NetApp Files Account where
            the capacity pool holding the volume exists
        capacitypool_name (string): Capacity pool name where volume will be
            created
        volume_name (string): Volume name
        volume_usage_quota (long): Volume size in bytes, minimum value is
            107374182400 (100GiB), maximum value is 109951162777600 (100TiB)
        service_level (string): Volume service level, needs to be the same as
            the capacity pool, valid values are "Ultra","Premium","Standard"
        subnet_id (string): Subnet resource id of the delegated to ANF Volumes
            subnet
        location (string): Azure short name of the region where resource will
            be deployed, needs to be the same as the account
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        Volume: Returns the newly created volume resource
    """

    volume_body = Volume(
        usage_threshold=volume_usage_quota,
        creation_token=volume_name,
        location=location,
        service_level=service_level,
        subnet_id=subnet_id,
        protocol_types=["NFSv3"],
        tags=tags)

    return client.volumes.begin_create_or_update(resource_group_name,
                                           anf_account_name,
                                           capacitypool_name,
                                           volume_name,
                                           volume_body).result()


def create_volume_from_snapshot(client, resource_group_name, anf_account_name,
                                capacitypool_name, volume, snapshot_id,
                                volume_name, tags=None):
    """Creates a volume from a snapshot

    Function that creates a volume from an existing snapshot. This example use
    the previous created volume that had a snapshot taken to gather some
    important information to create a new volume from the snapshot, noted in
    the volume_body object.

    Args:
        client (NetAppManagementClient): Azure Resource Provider
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            volume will be created, it needs to be the same as the account
        anf_account_name (string): Name of the Azure NetApp Files Account
            where the capacity pool holding the volume exists
        capacitypool_name (string): Capacity pool name where volume will be
            created
        volume (Volume): Original volume object where the snapshot was taken
        snapshot_id (string): UUID v4 name of the snapshot
        tags (object): Optional. Key-value pairs to tag the resource, default
            value is None. E.g. {'cc':'1234','dept':'IT'}

    Returns:
        Volume: Returns the newly created volume resource
    """


    volume_body = Volume(
        snapshot_id=snapshot_id,
        export_policy=volume.export_policy,
        usage_threshold=volume.usage_threshold,
        creation_token=volume_name,
        location=volume.location,
        service_level=volume.service_level,
        subnet_id=volume.subnet_id,
        protocol_types=volume.protocol_types,
        tags=tags)

    return client.volumes.begin_create_or_update(resource_group_name,
                                           anf_account_name,
                                           capacitypool_name,
                                           volume_name,
                                           volume_body).result()


def create_snapshot(client, resource_group_name, anf_account_name,
                    capacitypool_name, volume_name, snapshot_name,
                    location):
    """Creates a volume snapshot

    Function that creates a volume snapshot.

    Args:
        client (NetAppManagementClient): Azure Resource Provider 
            Client designed to interact with ANF resources
        resource_group_name (string): Name of the resource group where the
            snapshot will be created, it needs to be the same as the account
        anf_account_name (string): Name of the Azure NetApp Files Account where
            the capacity pool holding the volume exists
        capacitypool_name (string): Capacity pool name where volume to be taken
            the snapshot exists
        volume_name (string): Name of the volume to take the snapshot
        snapshot_name (string): Snapshot name
        location (string): Azure short name of the region where resource will
            be deployed, needs to be the same as the account

    Returns:
        Snapshot: Returns the newly created snapshot resource
    """

    snapshot_body = Snapshot(location=location)

    return client.snapshots.begin_create(resource_group_name,
                                   anf_account_name,
                                   capacitypool_name,
                                   volume_name,
                                   snapshot_name,
                                   snapshot_body).result()


def run_example():
    """Azure NetApp Files SDK management example."""

    print_header("Azure NetAppFiles Python SDK Sample - Sample "
        "project that performs CRUD management operations with Azure "
        "NetApp Files SDK with Python")

    # Creating the Azure NetApp Files Client with an Application
    # (service principal) token provider
    credentials, subscription_id = sample_utils.get_credentials()
    anf_client = NetAppManagementClient(
        credentials, subscription_id)

    # Checking if vnet/subnet information leads to a valid resource
    resources_client = ResourceManagementClient(credentials, subscription_id)
    SUBNET_ID = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'.format(
        subscription_id, VNET_RESOURCE_GROUP_NAME, VNET_NAME, SUBNET_NAME)

    result = resource_exists(resources_client, 
        SUBNET_ID, 
        VIRTUAL_NETWORKS_SUBNET_API_VERSION)

    if not result:
        console_output("ERROR: Subnet not with id {} not found".format(
            SUBNET_ID))
        raise Exception("Subnet not found error. Subnet Id {}".format(
            SUBNET_ID))


    # Creating an Azure NetApp Account
    console_output('Creating Azure NetApp Files account ...')
    account = None
    try:
        account = create_account(
            anf_client, RESOURCE_GROUP_NAME, ANF_ACCOUNT_NAME, LOCATION)
        console_output(
            '\tAccount successfully created, resource id: {}'.format(
                account.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Creating a Capacity Pool
    console_output('Creating Capacity Pool ...')
    capacity_pool = None
    try:
        capacity_pool = create_capacitypool_async(
            anf_client,
            RESOURCE_GROUP_NAME,
            account.name,
            CAPACITYPOOL_NAME,
            CAPACITYPOOL_SERVICE_LEVEL,
            CAPACITYPOOL_SIZE, LOCATION)

        console_output('\tCapacity Pool successfully created, resource id: {}'
                       .format(capacity_pool.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Creating a Volume
    #
    # Note: With exception of Accounts, all resources with Name property
    # returns a relative path up to the name and to use this property in
    # other methods, like Get for example, the argument needs to be
    # sanitized and just the actual name needs to be used (the hierarchy
    # needs to be cleaned up in the name).
    # Capacity Pool Name property example: "pmarques-anf01/pool01"
    # "pool01" is the actual name that needs to be used instead. Below you
    # will see a sample function that parses the name from its
    # resource id: resource_uri_utils.get_anf_capacity_pool()
    console_output('Creating a Volume ...')
    subnet_id = '/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Network/virtualNetworks/{}/subnets/{}'\
                .format(subscription_id,
                        VNET_RESOURCE_GROUP_NAME,
                        VNET_NAME,
                        SUBNET_NAME)
    volume = None
    try:
        pool_name = resource_uri_utils.get_anf_capacity_pool(capacity_pool.id)

        volume = create_volume(anf_client,
                               RESOURCE_GROUP_NAME,
                               account.name, pool_name,
                               VOLUME_NAME,
                               VOLUME_USAGE_QUOTA,
                               CAPACITYPOOL_SERVICE_LEVEL,
                               subnet_id,
                               LOCATION)

        console_output('\tVolume successfully created, resource id: {}'
                       .format(volume.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Creating a snapshot
    console_output('Creating a Snapshot ...')
    snapshot = None
    try:
        volume_name = resource_uri_utils.get_anf_volume(volume.id)

        snapshot = create_snapshot(anf_client,
                                   RESOURCE_GROUP_NAME,
                                   account.name,
                                   pool_name,
                                   VOLUME_NAME,
                                   SNAPSHOT_NAME,
                                   LOCATION)

        sample_utils.wait_for_anf_resource(anf_client, snapshot.id)

        console_output(
            '\tSnapshot successfully created, resource id: {}'
            .format(snapshot.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Creating a new volume from snapshot
    #
    # Note: SnapshotId is not the actual resource Id of the snapshot, this
    # value is the unique identifier (guid) of the snapshot, represented
    # by the SnapshotId instead.
    console_output('Creating New Volume from Snapshot ...')
    volume_from_snapshot = None
    try:
        new_volume_name = "Vol-{}".format(
            resource_uri_utils.get_anf_snapshot(snapshot.id))

        volume_from_snapshot = create_volume_from_snapshot(anf_client,
                                                           RESOURCE_GROUP_NAME,
                                                           account.name,
                                                           pool_name,
                                                           volume,
                                                           snapshot.snapshot_id,
                                                           new_volume_name)

        console_output('\tNew volume from snapshot successfully created, resource id: {}'.format(
            volume_from_snapshot.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Updating a Capacity Pool
    console_output('Performing updates on Capacity Pool and Volume...')
    new_capacity_pool_size_tib = 10
    console_output('\tChanging Capacity Pools size from {}TiB to {}TiB'.format(
        sample_utils.get_bytes_in_tib(capacity_pool.size),
        new_capacity_pool_size_tib))
    try:
        capacity_pool_patch = CapacityPoolPatch(location=capacity_pool.location,
                                                size=sample_utils.get_tib_in_bytes(new_capacity_pool_size_tib))

        capacity_pool = anf_client.pools.begin_update(RESOURCE_GROUP_NAME,
                                                account.name,
                                                resource_uri_utils.get_anf_capacity_pool(capacity_pool.id),
                                                capacity_pool_patch).result()

        console_output('\t\tCapacity Pool successfully updated, new size {}TiB, resource id: {}'.format(
            sample_utils.get_bytes_in_tib(capacity_pool.size), capacity_pool.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Volume updates: resize and adding a new export policy
    new_volume_size_tib = 1
    console_output('\tChanging volume size from {}TiB to {}TiB'.format(
        sample_utils.get_bytes_in_tib(volume.usage_threshold), new_volume_size_tib))

    # Getting list of export policies and adding a new one at the end
    rule_list = sorted(volume.export_policy.rules,
                       key=lambda r: r.rule_index, reverse=True)

    # Currently, ANF's volume export policy supports up to 5 rules
    export_policies_patch = None
    if len(rule_list) <= 4:
        rule_list.append(ExportPolicyRule(
            allowed_clients="10.0.0.4/32",
            cifs=False,
            nfsv3=True,
            nfsv41=False,
            rule_index=rule_list[0].rule_index + 1,
            unix_read_only=False,
            unix_read_write=True))

        export_policies_patch = VolumePatchPropertiesExportPolicy(
            rules=rule_list)

    if export_policies_patch is None:
        volume_patch = VolumePatch(
            location=volume.location,
            service_level=volume.service_level,
            usage_threshold=sample_utils.get_tib_in_bytes(new_volume_size_tib))
    else:
        volume_patch = VolumePatch(
            location=volume.location,
            service_level=volume.service_level,
            usage_threshold=sample_utils.get_tib_in_bytes(new_volume_size_tib),
            export_policy=export_policies_patch)

    try:
        updated_volume = anf_client.volumes.begin_update(RESOURCE_GROUP_NAME,
                                                   account.name,
                                                   resource_uri_utils.get_anf_capacity_pool(
                                                       capacity_pool.id),
                                                   resource_uri_utils.get_anf_volume(volume.id),
                                                   volume_patch).result()

        console_output('\t\tVolume successfully updated, new size: {}TiB, export policy count: {}, resource id: {}'
                       .format(sample_utils.get_bytes_in_tib(updated_volume.usage_threshold),
                               len(updated_volume.export_policy.rules),
                               updated_volume.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Retrieving resources
    console_output('Performing retrieval operations ...')

    # Accounts
    # Getting a list of ANF Accounts
    console_output('\tListing accounts...')
    account_list = None
    try:
        account_list = list(anf_client.accounts.list(RESOURCE_GROUP_NAME))

        for i, retrieved_account in enumerate(account_list):
            console_output('\t\t{} - Account Name: {}, Id: {}'
                           .format(i,
                                   retrieved_account.name,
                                   retrieved_account.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Getting a single ANF Account
    console_output('\tGetting a single account...')
    try:
        retrieved_account = anf_client.accounts.get(
            RESOURCE_GROUP_NAME, account.name)

        console_output('\t\tAccount Name: {}, Id: {}'.format(
            retrieved_account.name, retrieved_account.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Capacity Pools
    # Getting a list of capacity pools from an account
    console_output('\tListing capacity pools from account {}...'
                   .format(account.name))
    capacitypool_list = None
    try:
        capacitypool_list = list(anf_client.pools.list(RESOURCE_GROUP_NAME,
                                                       resource_uri_utils.get_anf_account(account.id)))

        for i, retrieved_pool in enumerate(capacitypool_list):
            console_output('\t\t{} - Capacity Pool Name: {}, Id: {}'
                           .format(i,
                                   retrieved_pool.name,
                                   retrieved_pool.id))

    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Getting a single capacity pool
    console_output('\tGetting a single capacity pool...')
    try:
        retrieved_pool = anf_client.pools.get(RESOURCE_GROUP_NAME,
                                              resource_uri_utils.get_anf_account(
                                                  account.id),
                                              resource_uri_utils.get_anf_capacity_pool(capacity_pool.id))

        console_output('\t\tCapacity Pool Name: {}, Id: {}'.format(
            retrieved_pool.name, retrieved_pool.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Volumes
    # Getting a list of volumes from a capacity pool
    console_output('\tListing volumes from capacity pool {}...'.format(
        capacity_pool.name))
    volume_list = None
    try:
        volume_list = list(anf_client.volumes.list(RESOURCE_GROUP_NAME,
                                                   resource_uri_utils.get_anf_account(
                                                       account.id),
                                                   resource_uri_utils.get_anf_capacity_pool(capacity_pool.id)))

        for i, retrieved_volume in enumerate(volume_list):
            console_output('\t\t{} - Volume Name: {}, Id: {}'
                           .format(i,
                                   retrieved_volume.name,
                                   retrieved_volume.id))

    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Getting a single volume
    console_output('\tGetting a single volume...')
    try:
        retrieved_volume = anf_client.volumes.get(RESOURCE_GROUP_NAME,
                                                  resource_uri_utils.get_anf_account(
                                                      account.id),
                                                  resource_uri_utils.get_anf_capacity_pool(
                                                      capacity_pool.id),
                                                  resource_uri_utils.get_anf_volume(volume.id))

        console_output('\t\tVolume Name: {}, Id: {}'.format(
            retrieved_volume.name, retrieved_volume.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Snapshots
    # Getting a list of snapshots from volume
    console_output(
        '\tListing snapshots from from volume {}...'.format(volume.name))
    snapshot_list = None
    try:
        snapshot_list = list(anf_client.snapshots.list(RESOURCE_GROUP_NAME,
                                                       resource_uri_utils.get_anf_account(
                                                           account.id),
                                                       resource_uri_utils.get_anf_capacity_pool(
                                                           capacity_pool.id),
                                                       resource_uri_utils.get_anf_volume(volume.id)))

        for i, retrieved_snapshot in enumerate(snapshot_list):
            console_output('\t\t{} - Snapshot Name: {}, Id: {}'
                           .format(i,
                                   retrieved_snapshot.name,
                                   retrieved_snapshot.id))

    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Getting a single snapshot
    console_output('\tGetting a single snapshot...')
    try:
        retrieved_snapshot = anf_client.snapshots.get(RESOURCE_GROUP_NAME,
                                                      resource_uri_utils.get_anf_account(
                                                          account.id),
                                                      resource_uri_utils.get_anf_capacity_pool(
                                                          capacity_pool.id),
                                                      resource_uri_utils.get_anf_volume(
                                                          volume.id),
                                                      resource_uri_utils.get_anf_snapshot(snapshot.id))

        console_output('\t\tSnapshot Name: {}, Id: {}'.format(
            retrieved_snapshot.name, retrieved_snapshot.id))
    except AzureError as ex:
        console_output(
            'An error ocurred. Error details: {}'.format(ex.message))
        raise

    # Cleaning up. This process needs to start the cleanup from the innermost
    # resources down in the hierarchy chain in our case
    # Snapshots->Volumes->Capacity Pools->Accounts
    if SHOULD_CLEANUP:
        console_output('Cleaning up...')

        # Cleaning up snapshot
        console_output(
            "\tWaiting for 1 minute to let the snapshot used to create a new \
            volume to complete the split operation therefore not being locked...")
        time.sleep(60)
        console_output("\tDeleting Snapshot {}...".format(
            resource_uri_utils.get_anf_snapshot(snapshot.id)))

        try:
            anf_client.snapshots.begin_delete(RESOURCE_GROUP_NAME,
                                        account.name,
                                        resource_uri_utils.get_anf_capacity_pool(
                                            capacity_pool.id),
                                        resource_uri_utils.get_anf_volume(
                                            volume.id),
                                        resource_uri_utils.get_anf_snapshot(snapshot.id)).wait()

            # ARM Workaround to wait the deletion complete/propagate
            sample_utils.wait_for_no_anf_resource(anf_client, snapshot.id)

            console_output('\t\tDeleted Snapshot: {}'.format(snapshot.id))
        except AzureError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise

        # Cleaning up volumes
        # Note: Volume deletion operations at the RP level are executed
        # serially
        console_output("\tDeleting Volumes...")
        try:
            volume_ids = [volume.id, volume_from_snapshot.id]
            for volume_id in volume_ids:
                console_output("\t\tDeleting {}".format(volume_id))
                anf_client.volumes.begin_delete(RESOURCE_GROUP_NAME,
                                          account.name,
                                          resource_uri_utils.get_anf_capacity_pool(
                                             capacity_pool.id),
                                          resource_uri_utils.get_anf_volume(volume_id)).wait()

                sample_utils.wait_for_no_anf_resource(anf_client, volume_id)

                console_output('\t\tDeleted Volume: {}'.format(volume_id))
        except AzureError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise

        # Cleaning up Capacity Pool
        console_output("\tDeleting Capacity Pool {} ...".format(
            resource_uri_utils.get_anf_capacity_pool(capacity_pool.id)))
        try:
            anf_client.pools.begin_delete(RESOURCE_GROUP_NAME,
                                    account.name,
                                    resource_uri_utils.get_anf_capacity_pool(
                                        capacity_pool.id)).wait()

            sample_utils.wait_for_no_anf_resource(anf_client, capacity_pool.id)

            console_output(
                '\t\tDeleted Capacity Pool: {}'.format(capacity_pool.id))
        except AzureError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise

        # Cleaning up Account
        console_output("\tDeleting Account {} ...".format(account.name))
        try:
            anf_client.accounts.begin_delete(RESOURCE_GROUP_NAME, account.name)
            sample_utils.wait_for_no_anf_resource(anf_client, account.id)
            console_output('\t\tDeleted Account: {}'.format(account.id))
        except AzureError as ex:
            console_output(
                'An error ocurred. Error details: {}'.format(ex.message))
            raise


# This script expects that the following environment var are set:
#
# AZURE_AUTH_LOCATION: contains path for azureauth.json file
#
# File content (and how to generate) is documented at
# https://docs.microsoft.com/en-us/dotnet/azure/dotnet-sdk-azure-authenticate?view=azure-dotnet

if __name__ == "__main__":

    run_example()
