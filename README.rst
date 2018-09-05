==========
github2cff
==========

Suite of scripts to produce a CFF formatted file (https://citation-file-format.github.io/) using project metadata from GitHub or GitLab.

Installation
------------

.. code-block:: bash

   pip install git+https://github.com/citation-file-format/github2cff

Usage
-----

.. code-block:: bash

   python gitlab_cff_extractor.py
   python github_cff_extractor.py

To create a CITATION.cff file of a release, you must supply the doi that is associated with the release.  Whenever a new release is made of the software being cited, the CITATION.cff must be updated with the new doi, version and release date.

github2cff was developed in around 6 hrs at the Software Sustainability Institute Collabrative Workshop 2018 Hackday.

License
-------

This software is licensed under version 2.0 of the Apache Software License.
