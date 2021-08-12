#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.readlines()

test_requirements = ['pytest>=3', ]

setup(
    author="Michael Graf",
    author_email='michael.graf@uni-tuebingen.de',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Generates FHIR synthetic fhir resources.",
    entry_points={
        'console_scripts': [
            'fhir_kindling=fhir_kindling.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='fhir_kindling',
    name='fhir_kindling',
    packages=find_packages(include=['fhir_kindling', 'fhir_kindling.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/migraf/fhir_kindling',
    version='0.1.0',
    zip_safe=False,
)
