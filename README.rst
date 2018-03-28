==========
github2cff
==========

Suite of scripts to citation file formatted file (https://citation-file-format.github.io/) from project data on GitHub or GitLab.

Free software: Apache Software License 2.0

Documentation: To do...

Installation
------------

#.. code-block:: bash
#
#    pip install git+https://github.com/citation-file-format/github2cff

Usage
-----

To create a CITATION.cff file of a release, you must supply the doi that is associated with the release.

.. code-block:: bash

   python gitlab_cff_extractor.py
   python github_cff_extractor.py

Whenever a new release is made of the software the CITATION.cff must be updated with new doi/version/release date.
