__author__ = 'dank'

import setuptools

PLUGIN_COMMONS_VERSION = '3.0'
PLUGIN_COMMONS_BRANCH = 'develop'
PLUGIN_COMMONS = 'https://github.com/cloudify-cosmo/cloudify-plugins-common' \
    '/tarball/{0}'.format(PLUGIN_COMMONS_BRANCH)

setuptools.setup(
    zip_safe=False,
    name='cloudify-puppet-plugin',
    version='1.0',
    author='ilya',
    author_email='ilya.sher@coding-knight.com',
    packages=['puppet_plugin'],
    license='LICENSE',
    description='Cloudify Chef plugin',
    install_requires=[
        "cloudify-plugins-common",
    ],
    package_data={
        'cloudify_plugin_puppet': ['puppet/facts/cloudify_facts.rb']
    },
    dependency_links=[
        "{0}#egg=cloudify-plugins-common-{1}".format(PLUGIN_COMMONS,
                                                     PLUGIN_COMMONS_VERSION)]
)

