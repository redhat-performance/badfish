import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="badfish",
    version="1.0.1",
    description="Badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhat-performance/badfish",
    install_requires=[
        "pyyaml>=3.10",
        "aiohttp>=3.7.4",
        "setuptools>=39.0",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(
        where="src",
        include=['helpers', 'badfish']
    ),
    project_urls={
        "Bug Tracker": "https://github.com/redhat-performance/badfish/issues",
        "Documentation": "https://github.com/redhat-performance/badfish/blob/master/README.md",
        "Source Code": "https://github.com/redhat-performance/badfish",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["badfish=badfish.badfish:main"]},
)
