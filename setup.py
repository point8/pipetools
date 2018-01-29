import os
from setuptools import setup

setup(
    name='pipedrive-backup',
    description='CLI script to backup a Pipedrive CRM instance',
    url='https://git.point-8.de/',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
    ],
    version='1',
    entry_points={
        'console_scripts': [
            'pipetools = pipetools:main',
        ]
    },
    install_requires=['tqdm', 'pendulum'],
)
