# -*- coding: utf-8 -*-
"""
:author: Pawel Chomicki
:contact: pawel.chomicki@nokia.com
"""


class VMConfigBuilder(object):
    """Virtual machine configuration builder.

    Based on command line parameters and Hiera configuration parameters generates virtual machine
    configuration object.

    ::

        builder = VMConfigBuilder(args, hiera)
        config = builder.build()

        config.name         # Get VM name
        config.ram          # Get VM ram
        config.cpu          # Get VM CPU
        config.password     # Get VM username password

        config.network.ip
        config.network.mask
        config.network.bc
        config.network.gw

        config.dns.ip
        config.dns.search

        config.pool.name
        config.pool.folder

        config.template.cloud_init
        config.template.kvm_config
        config.template.meta_data

        config.storage.ip
        config.storage.network
        config.storage.bc
        config.storage.mask

    """

    def __init__(self, cmd_args, hiera_config):
        """
        :param cmd_args: Object which contains command line parameters provided by the user.
        :param hiera_config: Object which contains Hiera YAML configuration parameters.
        """
        self._hiera_config = hiera_config
        self._cmd_args = cmd_args
        self._vm_config = VMConfig()

    def build(self):
        """Creates VM configuration file based."""
        self._vm_config.name = self._create_name()
        self._vm_config.network = self._create_net()
        self._vm_config.dns = self._create_dns()
        self._vm_config.pool = self._create_pool()
        self._vm_config.target = self._create_target()
        self._vm_config.storage = self._create_storage()
        return self._vm_config

    def _create_name(self):
        if self._cmd_args.name == 'dns' or self._cmd_args.name == 'puppet' or self._cmd_args.name == 'ceph-admin':
            return self._hiera_config.infra.name
        return self._hiera_config.stack.vm[self._cmd_args.name]

    def _create_net(self):
        config = VMConfig()
        config.ip = self._hiera_config.infra.network
        config.mask = self._hiera_config.infra.network_mask
        config.bc = self._hiera_config.infra.broadcast_network
        config.gw = self._hiera_config.infra.nework_gw
        return config

    def _create_dns(self):
        config = VMConfig()
        config.ip_ext = self._set_external_dns()
        config.ip_int = self._hiera_config.infra.dns
        config.ip = "{} {}".format(self._vm_config.ip_ext_dns, self._vm_config.ip_int_dns)
        config.search = self._hiera_config.stack.domain
        return config

    def _create_pool(self):
        config = VMConfig()
        config.ceph_pool_name = self._hiera_config.cephfs.pool
        config.default_pool = self._hiera_config.kvm.default.pool.name
        return config

    def _set_external_dns(self):
        raise Exception("Not implemented")

    def _create_target(self):
        raise Exception("Not implemented")

    def _create_storage(self):
        raise Exception("Not implemented")


class VMConfig(dict):
    """Virtual machine configuration object. This is dict like object with additional DOT syntax.

    ::

        vmconfig = VMConfig()
        vmconfig.something = '1'    # Set something attr. Equals vmconfig['something'] = '1'
        vmconfig.something          # Get something attr. Equals vmconfig['something']

    It is possible to made some nested configurations like below

    ::

        vmconfig = VMConfig()
        vmconfig.net = VMConfig()
        vmconfig.net.ip = '1.1.1.1'

    """
    def __setattr__(self, key, value):
        if key in self:
            raise AttributeError("Attribute {} can't be overridden.".format(key))
        self[key] = value

    def __getattr__(self, item):
        if item not in self:
            raise AttributeError("Attribute {} is not available.".format(item))
        return self[item]
