from setuptools import find_packages, setup

from entity.version import ENTITY_CLIENT_VERSION

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="moonstream-entity",
    version=ENTITY_CLIENT_VERSION,
    packages=find_packages(),
    package_data={"entity": ["py.typed"]},
    install_requires=["requests", "pydantic"],
    extras_require={
        "dev": [
            "black",
            "mypy",
            "isort",
        ],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Moonstream entity API client library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Moonstream",
    author_email="engineering@moonstream.to",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/bugout-dev/entity",
    entry_points={"console_scripts": ["entity=entity.cli:main"]},
)
