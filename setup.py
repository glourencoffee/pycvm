from setuptools import setup, find_packages
import versioneer

with open('README_en_US.md', mode='r', encoding='utf-8') as f:
    readme_en_us = f.read()

setup(name                          = 'pycvm',
      version                       = versioneer.get_version(),
      cmdclass                      = versioneer.get_cmdclass(),
      description                   = 'Python library for processing data from CVM',
      long_description              = readme_en_us,
      long_description_content_type = 'text/markdown',
      author                        = 'Giovanni L',
      author_email                  = 'callmegiorgio@hotmail.com',
      url                           = 'https://github.com/callmegiorgio/pycvm/',
      license                       = 'MIT',
      packages                      = find_packages(),
      keywords                      = ['investment', 'finances'],
      install_requires              = [],
      python_requires               = '>=3.7'
)