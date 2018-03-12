#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name="bootstrap",
    version="0.1.0",
    package_dir={
        "": "lib"
    },
    packages=find_packages("lib"),

    entry_points={
        "console_scripts": [
            "bs = bootstrap.exec.driver:main"
        ]
    },

    author="Triston Whetten",
    description="Manage yocto layouts with multiple repositories/layers. Based on dev-pipeline written by Stephen Newell",
    license="BSD-2",
    url="https://github.com/crazyorc/dev-pipeline",
)
