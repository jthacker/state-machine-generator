from setuptools import setup

# Load __version__ without importing it (avoids race condition with build)
exec(open('smg/version.py').read())

setup(name='smg',
      description='A minimal boilerplate, state machine generator',
      packages=['smg'],
      version=__version__,
      url='https://github.com/jthacker/state-machine-generator',
      download_url='https://github.com/jthacker/state-machine-generator/archive/v{}.tar.gz'.format(__version__),
      author='jthacker',
      author_email='thacker.jon@gmail.com',
      keywords=['state machine'],
      classifiers=[],
      install_requires=[
          'jinja2>=2.8',
          'ply>=3.9',
          'pyaml',
          'terseparse>=1.1.3',
          ],
      tests_require=[
          'pytest'
          ],
      setup_requires=[
          'pytest-runner'
          ],
      entry_points = {
          'console_scripts': [
              'smg=smg.bin:main'
          ]},
      long_description="")
