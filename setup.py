import setuptools
import re
import os

here = os.path.abspath(os.path.dirname(__file__))
version_file = os.path.join(here, "src", "badfish", "__init__.py")

with open(version_file, "r", encoding="utf-8") as f:
    content = f.read()
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", content, re.M)
    if match:
        current_version = match.group(1)
    else:
        raise RuntimeError("Unable to find version string in src/badfish/__init__.py")

setuptools.setup(version=current_version)
