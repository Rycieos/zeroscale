from setuptools import find_packages, setup

with open("README.md", 'r') as fh:
    long_description = fh.read()

setup(
    name="zeroscale",
    version="0.1.0",
    author="Mark Vander Stel",
    author_email="mvndrstl@gmail.com",
    description="Scale-to-zero any server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rycieos/zeroscale",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "zeroscale = zeroscale.__main__:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
    ],
)
