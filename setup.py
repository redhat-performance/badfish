import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="badfish",
    version="1.0.0",
    description="Badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhat-performance/badfish",
    install_requires=[
        "pyyaml>=4.2b1",
        "aiohttp==3.7.4",
        "async-lru==1.0.2",
        "setuptools~=46.1.3",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    project_urls={
        "Bug Tracker": "https://github.com/redhat-performance/badfish/issues",
        "Documentation": "https://github.com/redhat-performance/badfish/blob/master/README.md",
        "Source Code": "https://github.com/redhat-performance/badfish",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["badfish=badfish.badfish:main"]},
)
