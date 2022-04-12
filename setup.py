from setuptools import setup

setup(
    name='trollhub',
    version='0.1.2',
    packages=['trollhub'],
    include_package_data=True,
    install_requires=[
        'flask', 'pyyaml', 'trollsift', 'waitress',
    ],
    scripts=['bin/start-trollhub.py', ],

)
