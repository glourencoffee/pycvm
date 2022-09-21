from setuptools import setup
import versioneer

with open('README_en_US.md') as f:
    readme_en_us = f.read()

setup(name                          = 'cvm',
      version                       = versioneer.get_version(),
      cmdclass                      = versioneer.get_cmdclass(),
      description                   = 'Python library for processing data from CVM',
      long_description              = readme_en_us,
      long_description_content_type = 'text/markdown',
      author                        = 'Giovanni L',
      author_email                  = 'callmegiorgio@hotmail.com',
      url                           = 'https://github.com/callmegiorgio/cvm/',
      license                       = 'MIT',
      packages                      = ['cvm'],
      keywords                      = ['investment', 'finances'],
      install_requires              = [],
      python_requires               = '>=3.7'
)