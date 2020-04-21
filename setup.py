import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Badfish-quads", # Replace with your own username
    version="0.0.1",
    description="Badfish is a Redfish-based API tool for managing bare-metal systems via the Redfish API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redhat-performance/badfish",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
