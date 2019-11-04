# resource_uri_utils.py Code Sample
#
# Copyright (c) Microsoft and contributors.  All rights reserved.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


def get_resource_value(resource_uri, resource_name):
    """Gets the resource name based on resource type

    Function that returns the name of a resource from resource id/uri based on
    resource type name.

    Args:
        resource_uri (string): resource id/uri
        resource_name (string): Name of the resource type, e.g. capacityPools

    Returns:
        string: Returns the resource name
    """

    if not resource_uri.strip():
        return None

    if not resource_name.startswith('/'):
        resource_name = '/{}'.format(resource_name)

    if not resource_uri.startswith('/'):
        resource_uri = '/{}'.format(resource_uri)

    # Checks to see if the ResourceName and ResourceGroup is the same name and
    # if so handles it specially.
    rg_resource_name = '/resourceGroups{}'.format(resource_name)
    rg_index = resource_uri.lower().find(rg_resource_name.lower())
    # dealing with case where resource name is the same as resource group
    if rg_index > -1:
        removed_same_rg_name = resource_uri.lower().split(
            resource_name.lower())[-1]
        return removed_same_rg_name.split('/')[1]

    index = resource_uri.lower().find(resource_name.lower())
    if index > -1:
        res = resource_uri[index + len(resource_name):].split('/')
        if len(res) > 1:
            return res[1]

    return None


def get_resource_name(resource_uri):
    """Gets the resource name from resource id/uri

    Function that returns the name of a resource from resource id/uri, this is
    independent of resource type

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the resource name
    """

    if not resource_uri.strip():
        return None

    position = resource_uri.rfind('/')
    return resource_uri[position + 1:]


def get_resource_group(resource_uri):
    """Gets the resource group name from resource id/uri

    Function that returns the resource group name from resource id/uri

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the resource group name
    """

    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/resourceGroups')


def get_subscription(resource_uri):
    """Gets the subscription id from resource id/uri

    Function that returns the resource group name from resource id/uri

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the subcription id (GUID)
    """

    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/subscriptions')


def get_anf_account(resource_uri):
    """Gets an account name from resource id/uri

    Function that returns the ANF acount name from resource id/uri

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the account name
    """

    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/netAppAccounts')


def get_anf_capacity_pool(resource_uri):
    """Gets pool name from resource id/uri

    Function that returns the capacity pool name from resource id/uri

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the capacity pool name
    """

    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/capacityPools')


def get_anf_volume(resource_uri):
    """Gets volume name from resource id/uri

    Function that returns the volume name from resource id/uri

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the volume name
    """

    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/volumes')


def get_anf_snapshot(resource_uri):
    """Gets snapshot name from resource id/uri

    Function that returns the snapshot name from resource id/uri

    Args:
        resource_uri (string): resource id/uri

    Returns:
        string: Returns the snapshot name
    """

    if not resource_uri.strip():
        return None

    return get_resource_value(resource_uri, '/snapshots')


def is_anf_resource(resource_uri):
    """Checks if resource is an ANF related resource

    Function verifies if the resource referenced in the resource id/uri is an
    ANF related resource

    Args:
        resource_uri (string): resource id/uri

    Returns:
        boolean: Returns true if resource is related to ANF or false otherwise
    """

    if not resource_uri.strip():
        return False

    return resource_uri.find('/providers/Microsoft.NetApp/netAppAccounts') > -1


def is_anf_snapshot(resource_uri):
    """Checks if resource is a snapshot

    Function verifies if the resource referenced in the resource id/uri is a
    snapshot

    Args:
        resource_uri (string): resource id/uri

    Returns:
        boolean: Returns true if resource is a snapshot
    """

    if (not resource_uri.strip()) or (not is_anf_resource(resource_uri)):
        return False

    return resource_uri.rfind('/snapshots/') > -1


def is_anf_volume(resource_uri):
    """Checks if resource is a volume

    Function verifies if the resource referenced in the resource id/uri is a
    volume

    Args:
        resource_uri (string): resource id/uri

    Returns:
        boolean: Returns true if resource is a volume
    """
    
    if (not resource_uri.strip()) or (not is_anf_resource(resource_uri)):
        return False

    return (resource_uri.rfind('/snapshots/') == -1) \
        and (resource_uri.rfind('/volumes/') > -1)


def is_anf_capacity_pool(resource_uri):
    """Checks if resource is a capacity pool

    Function verifies if the resource referenced in the resource id/uri is a
    capacity pool

    Args:
        resource_uri (string): resource id/uri

    Returns:
        boolean: Returns true if resource is a capacity pool
    """

    if (not resource_uri.strip()) or (not is_anf_resource(resource_uri)):
        return False

    return (resource_uri.rfind('/snapshots/') == -1) \
        and (resource_uri.rfind('/volumes/') == -1) \
        and (resource_uri.rfind('/capacityPools/') > -1)


def is_anf_account(resource_uri):
    """Checks if resource is an account

    Function verifies if the resource referenced in the resource id/uri is an
    account

    Args:
        resource_uri (string): resource id/uri

    Returns:
        boolean: Returns true if resource is an account
    """

    if (not resource_uri.strip()) or (not is_anf_resource(resource_uri)):
        return False

    return (resource_uri.rfind('/snapshots/') == -1) \
        and (resource_uri.rfind('/volumes/') == -1) \
        and (resource_uri.rfind('/capacityPools/') == -1) \
        and (resource_uri.rfind('/backupPolicies/') == -1) \
        and (resource_uri.rfind('/netAppAccounts/') > -1)
