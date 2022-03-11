#!/usr/bin/env python

"""The setup script."""
from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("CHANGELOG.md") as history_file:
    history = history_file.read()

test_requirements = [
    "pytest>=3",
]

setup(
    author="Michael Graf",
    author_email="michael.graf@uni-tuebingen.de",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="CRUD Operations against FHIR servers, resource validation and synthetic FHIR resource generation.",
    entry_points={"console_scripts": ["fhir_kindling=fhir_kindling.cli.cli:main", ], },
    long_description=readme + history,
    long_description_content_type="text/markdown",
    install_requires=[
        "python-dotenv",
        "pandas",
        "fhir.resources",
        "requests",
        "requests-oauthlib",
        "pendulum",
        "tqdm",
        "orjson",
        "pyyaml",
        "xmltodict",
        "pydantic",
        "click",
        "networkx"
    ],
    license="MIT license",
    include_package_data=True,
    keywords="fhir_kindling, fhir, pydantic, health, data, hl7",
    name="fhir_kindling",
    packages=find_packages(include=["fhir_kindling", "fhir_kindling.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/migraf/fhir-kindling",
    version='0.7.3',
    zip_safe=False,
)
