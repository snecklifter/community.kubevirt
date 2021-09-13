from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest
from kubernetes.dynamic.resource import Resource

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.community.kubevirt.tests.unit.compat.mock import MagicMock

from ansible_collections.kubernetes.core.plugins.module_utils.common import K8sAnsibleMixin, get_api_client
from ansible_collections.community.kubevirt.plugins.module_utils.kubevirt import KubeVirtRawModule


RESOURCE_DEFAULT_ARGS = {'api_version': 'v1alpha3', 'group': 'kubevirt.io',
                         'prefix': 'apis', 'namespaced': True}


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught
    by the test case"""
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __getitem__(self, attr):
        return getattr(self, attr)


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught
    by the test case"""
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def __getitem__(self, attr):
        return getattr(self, attr)


def exit_json(*args, **kwargs):
    kwargs['success'] = True
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(**kwargs)


def fail_json(*args, **kwargs):
    kwargs['success'] = False
    raise AnsibleFailJson(**kwargs)


@pytest.fixture()
def base_fixture(monkeypatch):
    monkeypatch.setattr(
        AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(
        AnsibleModule, "fail_json", fail_json)
    # Create mock methods in Resource directly, otherwise dyn client
    # tries binding those to corresponding methods in DynamicClient
    # (with partial()), which is more problematic to intercept
    kubernetes.dynamic.resource.Resource.get = MagicMock()
    kubernetes.dynamic.resource.Resource.create = MagicMock()
    kubernetes.dynamic.resource.Resource.delete = MagicMock()
    kubernetes.dynamic.resource.Resource.patch = MagicMock()
    kubernetes.dynamic.resource.Resource.search = MagicMock()
    kubernetes.dynamic.resource.Resource.watch = MagicMock()
    # Globally mock some methods, since all tests will use this
    K8sAnsibleMixin.patch_resource = MagicMock()
    K8sAnsibleMixin.patch_resource.return_value = ({}, None)
    K8sAnsibleMixin.get_api_client = MagicMock()
    K8sAnsibleMixin.get_api_client.return_value = None
    K8sAnsibleMixin.find_resource = MagicMock()
    KubeVirtRawModule.find_supported_resource = MagicMock()
