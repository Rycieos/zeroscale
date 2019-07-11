from setuptools import find_packages, setup

setup(
    name='zeroscale',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'zeroscale = zeroscale.__main__:main'
        ]
    },
)
