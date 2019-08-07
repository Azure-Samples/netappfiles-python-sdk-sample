# resource_uri_utils.py Code Sample
#
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

def get_resource_value(resource_uri, resource_name):
    if not resource_uri.strip():
        return None

    if not resource_name.startswith('/'):
        resource_name = '/{}'.format(resource_name)

    if not resource_uri.startswith('/'):
        resource_uri = '/{}'.format(resource_uri)

    # Checks to see if the ResourceName and ResourceGroup is the same name and if so handles it specially. 
    rg_resource_name = '/resourceGroups{}'.format(resource_name)
    rg_index = resource_uri.lower().find(rg_resource_name.lower())
    if rg_index > -1: # dealing with case where resource name is the same as resource group
        removed_same_rg_name = resource_uri.lower().split(resource_name.lower())[-1]
        return removed_same_rg_name.split('/')[1]

    index = resource_uri.lower().find(resource_name.lower())
    if index > -1:
        res = resource_uri[index + len(resource_name):].split('/')
        if len(res) > 1:
            return res[1]

    return None

def get_resource_name(resource_uri):
    if not resource_uri.strip():
        return None

    position = resource_uri.rfind('/')
    return resource_uri[position + 1:]


def get_resource_group(resource_uri):
    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/resourceGroups')


def get_subscription(resource_uri):
    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/subscriptions')


def get_anf_account(resource_uri):
    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/netAppAccounts')


def get_anf_capacitypool(resource_uri):
    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/capacityPools')


def get_anf_volume(resource_uri):
    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/volumes')


def get_anf_snapshot(resource_uri):
    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/snapshots')

def is_anf_resource(resource_uri):
    if not resource_uri.strip():
        return None

    return resource_uri.find('/providers/Microsoft.NetApp/netAppAccounts') > -1