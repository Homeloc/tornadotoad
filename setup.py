from setuptools import setup

setup(
    name = 'tornadotoad',
    packages = ['tornadotoad'],
    version = '0.3.5-homeloc',
    author='Ivan Kanevski',
    author_email='kanevski@gmail.com',
    url='https://github.com/kanevski/tornadotoad',
    description="Provides integration of hoptoad's exception notification service into a tornado app.",
    license="https://github.com/kanevski/tornadotoad/blob/master/LICENSE.txt",
    install_requires = [
        'tornado',
    ],
)
