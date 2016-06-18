#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='kvm-domain-backup',
      version='0.3.3',
      description='Script to backup KVM domains (through libvirt)',
      url='',
      author='Manuel Lorenzo Frieiro',
      author_email='mlorenzofr@gmail.com',
      maintainer='Manuel Lorenzo Frieiro',
      maintainer_email='mlorenzofr@gmail.com',
      license='BSD',
      keywords='backup libvirt kvm',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Archiving :: Backup',
          'Topic :: Utilities'
      ],
      packages=['kvm_domain_backup'],
      install_requires=[
          'libvirt-python'
      ],
      entry_points={
          'console_scripts':
              ['kvm-domain-backup = kvm_domain_backup.__main__:main']
      },
      zip_safe=False)
