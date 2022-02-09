from setuptools import setup

setup(
    name='trollhub',
    version='0.0.4',
    packages=['trollhub'],
    include_package_data=True,
    install_requires=[
        'flask', 'pyyaml', 'trollsift', 'waitress',
    ],
    scripts=['bin/start-trollhub.py', ],

)
