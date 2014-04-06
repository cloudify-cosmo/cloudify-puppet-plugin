import copy

from cloudify.decorators import operation as _operation

from cloudify_plugin_puppet.manager import (PuppetParamsError,
                                            PuppetManager,
                                            PUPPET_TAG_RE)

EXPECTED_OP_PREFIXES = (
    'cloudify.interfaces.lifecycle',
    'cloudify.interfaces.relationship_lifecycle')


def _extract_op(ctx):
    prefix, _, op = ctx.operation.rpartition('.')
    if prefix not in EXPECTED_OP_PREFIXES:
        ctx.logger.warn("Node operation is expected to start with '{0}' "
                        "but starts with '{1}'".format(
                            ' or '.join(EXPECTED_OP_PREFIXES), prefix))
    return op


@_operation
def operation(ctx, **kwargs):

    op = _extract_op(ctx)
    props = ctx.properties['puppet_config']
    tags = copy.deepcopy(props.get('tags', []))
    for tag in tags:
        if not PUPPET_TAG_RE.match(tag):
            raise PuppetParamsError(
                "puppet_config.tags[*] must match {0}, you gave "
                "'{1}'".format(PUPPET_TAG_RE, tag))
    if props.get('add_operation_tag', False):
        tags += ['cloudify_operation_' + op]

    ops_tags = props.get('operations_tags')
    if ops_tags:
        op_tags = ops_tags.get(op, [])
        if isinstance(op_tags, basestring):
            op_tags = [op_tags]
        if not isinstance(op_tags, list):
            raise PuppetParamsError(
                "Operation tags must be a list, not {0}".format(op_tags))
        if op_tags:
            ctx.logger.info("Operation '{0}' -> tags {1}".format(
                op, op_tags))
            tags += op_tags
        else:
            ctx.logger.info("No tags specific to operation '{0}', skipping".
                            format(op))
            return
    else:
        # Only run on "start"
        if op != 'start':
            return

    mgr = PuppetManager(ctx)
    # print(tags)
    mgr.run(tags=tags)

if __name__ == '__main__':
    import datetime
    from cloudify.mocks import MockCloudifyContext
    ctx = MockCloudifyContext(
        node_name='node_name',
        node_id=datetime.datetime.utcnow().strftime('node_name_%Y%m%d_%H%M%S'),
        operation='cloudify.interfaces.lifecycle.create',
        properties={
            'puppet_config': {
                'add_operation_tag': True,
                'operations_tags': {
                    'create': ['op_tag_create', 'tag2'],
                },
                'environment': 'e1',
                'tags': ['a', 'b'],
                'server': 'puppet',
                'node_name_prefix': 'pfx-',
                'node_name_suffix': '.puppet.example.com',
            }
        })

    operation(ctx)
