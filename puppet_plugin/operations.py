""" Puppet plugin operations. The code that handles puppet_config is split
into two parts. The part that does transformations such as extract
per-operation info resides in this file. Rest of the properties are handled
in manager.py """

import copy

from cloudify.decorators import operation as _operation

from puppet_plugin.manager import (PuppetParamsError,
                                   PuppetManager,
                                   PuppetAgentRunner,
                                   PuppetStandaloneRunner,
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


def _op_specifc(ctx, props, op, prop):

    if prop in props:
        e = props[prop]
        ctx.logger.info("Found {0} in properties".format(prop))
        if isinstance(e, dict):
            ctx.logger.info("Detected per-operation '{0}' in properties".
                            format(prop))
            if op in e:
                e = e[op]
            else:
                e = None
                ctx.logger.info("No '{0}' for operation '{1}'".
                                format(prop, op))
    else:
        e = None


def _prepare_tags(ctx, props, op):
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
            return None
    return tags


@_operation
def operation(ctx, **kwargs):

    op = _extract_op(ctx)
    props = ctx.properties['puppet_config']

    mgr = PuppetManager(ctx)
    tags = _prepare_tags(ctx, props, op)

    if isinstance(mgr, PuppetAgentRunner):
        if op != 'start' and tags is None:
            ctx.logger.info("No tags specific to operation '{0}', skipping".
                            format(op))
            return
        mgr.run(tags=tags)

    if isinstance(mgr, PuppetStandaloneRunner):
        e = _op_specifc(ctx, props, op, 'execute')
        m = _op_specifc(ctx, props, op, 'manifest')

        if e and m:
            raise RuntimeError("Either 'execute' or 'manifest' " +
                               "must be specified for given operation. " +
                               "Both are specified for operation {0}".format(
                                   op))
        mgr.run(tags=(tags or []), execute=e, manifest=m)

    raise RuntimeError("Internal error: unknown Puppet Runner")
