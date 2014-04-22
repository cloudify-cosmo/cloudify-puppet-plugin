import datetime
import re
import unittest

from cloudify.mocks import MockCloudifyContext
import puppet_plugin.operations
operation = puppet_plugin.operations.operation
from puppet_plugin.manager import DebianPuppetManager


# Warning: Singleton
class MockPuppetManager(object):
    """ Captures tags that Puppet would run with """
    tags = None

    def __init__(self, ctx):
        pass

    def run(self, tags):
        self.__class__.tags = tags


class PuppetTest(unittest.TestCase):

    server = 'puppet-master-server-name'

    def setUp(self):
        puppet_plugin.operations.PuppetManager = MockPuppetManager

    def _make_context(self, properties={}, operation='create'):
        props = {
            'server': self.server
        }
        props.update(properties)
        t = 'node_name_%Y%m%d_%H%M%S'
        ctx = MockCloudifyContext(
            node_name='node_name',
            node_id=datetime.datetime.utcnow().strftime(t),
            operation='cloudify.interfaces.lifecycle.' + operation,
            properties={
                'puppet_config': props
            })
        return ctx

    def test_operation_tag(self):

        def is_operation_tag(tag):
            return tag.startswith('op_tag_')

        for op in 'create', 'delete':
            ctx = self._make_context(
                properties={
                    'operations_tags': {
                        'create': 'op_tag_create',
                        'delete': ['op_tag_delete'],
                    }
                },
                operation=op
            )
            operation(ctx)
            self.assertIn('op_tag_' + op, MockPuppetManager.tags)
            operation_tags_count = len(
                filter(is_operation_tag, MockPuppetManager.tags))

            self.assertEqual(operation_tags_count, 1)

    def test_add_operation_tag(self):
            ctx = self._make_context(operation='start')
            operation(ctx)
            self.assertNotIn('cloudify_operation_start',
                             MockPuppetManager.tags)

            ctx = self._make_context(
                operation='start',
                properties={
                    'add_operation_tag': True,
                },
            )
            operation(ctx)
            self.assertIn('cloudify_operation_start', MockPuppetManager.tags)

    def _get_config_file(self, *args, **kwargs):
        ctx = self._make_context(*args, **kwargs)
        mgr = DebianPuppetManager(ctx)
        conf = mgr._get_config_file_contents()
        return conf

    def _match_in_config(self, re_, *args, **kwargs):
        conf = self._get_config_file(*args, **kwargs)
        print(conf)
        ok = re.search(re_, conf, re.MULTILINE)
        self.assertTrue(ok, "Regex in config not found: "+re_)
        

    def test_environment(self):
        e = 'puppetenv590b430c9f994fa5aebd93f224bb8b7f'

        re = '^\s*environment\s*=\s*' + e

        self._match_in_config(re,
                              properties={
                                  'environment': e,
                              })

    def test_server(self):
        re = '^\s*server\s*=\s*' + self.server
        self._match_in_config(re,
                              properties={
                                  'environment': 'e1',
                              })
        

    def test_pfx_sfx(self):
        for config_key in 'certname', 'node_name_value':
            re = '^\s*'+config_key+'\s*=.*nodepfx.*nodesfx$'
            self._match_in_config(re,
                                  properties={
                                      'environment': 'e1',
                                      'node_name_prefix': 'nodepfx',
                                      'node_name_suffix': 'nodesfx',
                                  })
        

    def test_tags(self):
        tags = ['t1', 't2']
        ctx = self._make_context(
            operation='start',
            properties={
                'tags': tags,
            },
        )
        operation(ctx)
        for tag in tags:
            self.assertIn(tag, MockPuppetManager.tags)
