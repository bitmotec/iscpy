"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from os import path as osPath

__version__ = "1.9.0"

setup(
    name="iscpy",
    version=__version__,
    description="Python library to parse ISC style config files.",
    long_description="""\
        ISCpy is a robust ISC config file parser. It has virtually unlimited
        possibilities for depth and quantity of ISC config files. ISC config
        files include BIND and DHCP config files among a few others.
    """,
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux"
        ],
    keywords="isc config bind dhcp parser lease dns python",
    python_requires='>=3.5, <4',
    author="Marc Averbeck",
    author_email="averbeck@github.com",
    url="https://github.com/bitmotec/iscpy",
    license="BSD 3-Clause",
    packages=find_packages(exclude=["ez_setup"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points="""
    """,
    project_urls={ # Optional
        'Bug Reports': 'https://github.com/bitmotec/iscpy/issues',
        'Source': 'https://github.com/bitmotec/iscpy',
    },
)
