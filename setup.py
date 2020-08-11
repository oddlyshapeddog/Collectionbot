from setuptools import setup

setup(name='artbot',
      version='0.1',
      description='Artbot',
      url='http://github.com/oddlyshapeddog/Collectionbot',
      author='Ciy-e',
      author_email='unknown@example.com',
      license='Unknown',
      packages=['artbot'],
      install_requires=[
          'discord',
          'logging',
          'concurrent',
          'simplejson',
          'asyncio',
          'pytz',
          'sqlalchemy',
          'apscheduler',
          'zipfile',
      ],
      zip_safe=False)
