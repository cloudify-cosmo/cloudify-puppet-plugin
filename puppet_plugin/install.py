# This is used for system tests.
# Installs Puppet.

from cloudify.decorators import operation as _operation

from puppet_plugin.manager import PuppetManager

@_operation
def operation(ctx, **kwargs):
    mgr = PuppetManager(ctx)
    mgr.install()
