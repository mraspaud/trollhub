from setuptools import setup

setup(
    name='trollhub',
    version='0.0.3',
    packages=['trollhub'],
    include_package_data=True,
    install_requires=[
        'flask', 'yaml', 'trollsift',
    ],
)
