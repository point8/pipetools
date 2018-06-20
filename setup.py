import os
from setuptools import setup

setup(
    name="pipetools",
    description="CLI script to interact with a Pipedrive CRM instance",
    url="https://github.com/point8/pipetools",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3 :: Only",
    ],
    version="1",
    packages=['pipetools'],
    entry_points={"console_scripts": ["pipetools = pipetools:main"]},
    install_requires=["tqdm", "pendulum"],
)
