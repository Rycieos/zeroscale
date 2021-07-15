#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = [
    "coveralls>=2.0,<3.0",
    "pytest>=5.4,<6.0",
    "pytest-asyncio>=0.12.0,<0.13.0",
    "pytest-cov>=2.6.1,<3.0",
]
docker_deps = [
    "docker>=4.0,<5.0",
]

setup(
    name="zeroscale",
    version="0.5.1",
    author="Mark Vander Stel",
    author_email="mvndrstl@gmail.com",
    description="Scale-to-zero any server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rycieos/zeroscale",
    packages=find_packages(),
    include_package_data=True,
    tests_require=test_deps,
    extras_require={
        "test": test_deps,
        "docker": docker_deps,
    },
    zip_safe=False,
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "zeroscale = zeroscale.__main__:main",
            "docker-zeroscale = zeroscale.__docker__:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
