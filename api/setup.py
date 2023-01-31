from setuptools import find_packages, setup

with open("entityapi/version.txt") as ifp:
    VERSION = ifp.read().strip()

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="entityapi",
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        "bugout>=0.2.4",
        "fastapi",
        "psycopg2-binary",
        "pydantic",
        "sqlalchemy",
        "uvicorn",
        "web3login>=0.0.4",
    ],
    extras_require={
        "dev": ["alembic", "black", "mypy", "isort"],
        "distribute": ["setuptools", "twine", "wheel"],
    },
    description="Moonstream entity API",
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
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "entityapi=entityapi.cli:main",
        ]
    },
    package_data={"entityapi": ["contracts/*.json"]},
    include_package_data=True,
)
