import setuptools

setuptools.setup(
    install_requires=[
        "pyyaml>=3.10",
        "aiohttp>=3.7.4",
        "setuptools>=42.0",
        "pillow>=5.1.0",
    ],
    entry_points={"console_scripts": ["badfish=badfish.badfish:main"]},
)
