#!/usr/bin/env python

from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

test_deps = [
    "coveralls>=1.4.0",
    "pytest>=5.0.0",
    "pytest-asyncio>=0.10.0",
    "pytest-cov>=2.6.1",
]

setup(
    name="zeroscale",
    version="0.2.0",
    author="Mark Vander Stel",
    author_email="mvndrstl@gmail.com",
    description="Scale-to-zero any server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rycieos/zeroscale",
    packages=find_packages(),
    include_package_data=True,
    tests_require=test_deps,
    extras_require={"test": test_deps},
    zip_safe=False,
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "zeroscale = zeroscale.__main__:main"
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
    ],
)
