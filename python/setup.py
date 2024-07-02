from setuptools import setup
from setuptools.command.build_py import build_py
from distutils.spawn import spawn, find_executable

class Build(build_py):
    def run(self):
        spawn([find_executable('protoc'), '--python_out=.', 'common/message.proto'])
        build_py.run(self)

setup(
    name='async_io',
    version='1.0.0',
    author='R&EC SPb ETU',
    author_email='info@nicetu.spb.ru',
    url='http://nicetu.spb.ru',
    description='Клиент-серверное взаимодействие по Protobuf/TCP с применением асинхронного подхода',
    long_description="",
    zip_safe=False,
    packages=['common', 'async_client', 'async_server'],
    cmdclass={
        'build_py': Build
    },
)
