__author__ = 'dank'

import setuptools

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
        'cloudify-plugins-common==3.0',
    ],
    package_data={
        'puppet_plugin': ['puppet/facts/cloudify_facts.rb']
    },
)
