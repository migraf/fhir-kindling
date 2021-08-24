=============
fhir-kindling
=============


.. image:: https://img.shields.io/pypi/v/fhir_kindling.svg
        :target: https://pypi.python.org/pypi/fhir_kindling

.. image:: https://img.shields.io/travis/migraf/fhir_kindling.svg
        :target: https://travis-ci.com/migraf/fhir_kindling

.. image:: https://readthedocs.org/projects/fhir-kindling/badge/?version=latest
        :target: https://fhir-kindling.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Generates FHIR synthetic fhir resources and data sets using a command line interface or predefined :code:`.yml`


* Free software: MIT license
* Documentation: https://fhir-kindling.readthedocs.io.


Installation
------------
Clone the repository and install using pip
..code-block:: bash

    cd fhir kindling
    pip install .


the :code:`fhir_kindling` command should now be available in you shell. Run :code:`fhir_kindling --help` to test it.

Features
--------

* Generate data sets using a step by step command line interface
.. code-block:: bash
    fhir_kindling generate

* Load and save generation options as `.yaml` files
* Upload and manage data sets on a FHIR server using the REST API

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
