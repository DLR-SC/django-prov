.. SPDX-FileCopyrightText: 2026 German Aerospace Center (DLR)
.. SPDX-FileContributor: Benjamin Moritz Bauer <benjamin.bauer@dlr.de>
..
.. SPDX-License-Identifier: MIT

.. _config-output:

How to correctly configure the output
=====================================

You can specify an output path, several serialization formats and graphical output formats.

This part of configuration belongs to the ``"OUTPUT"`` section in the configuration dictionary of your Django app.
The ``"OUTPUT"`` section has to be a dictionary itself. It may have the following keys:

1. ``"PATH"`` - The path were the output files will be written to (type: string). Provenance documents are printed to the command line if set to None.

2. ``"SERIALIZE"`` - The serialization format/s of your provenance documents. At least one format is mandatory. Can be a single format (type: string) or a list of the following:
    - ``provn`` - `The Provenance Notation`_
    - ``xml`` - `The PROV XML Schema`_
    - ``json`` - `The PROV-JSON Serialization`_
    - ``rdf`` - `The PROV Ontology`_

3. ``"GRAPHIC"`` - The graphical output formats if you want to plot your provenance documents. Can be a single format (type: string) or a list of the following:
    - ``svg`` - Scalable Vector Graphics
    - ``png`` - Portable Network Graphics
    - ``pdf`` - Portable Document Format


.. _The Provenance Notation: https://www.w3.org/TR/2013/REC-prov-n-20130430/
.. _The PROV XML Schema: https://www.w3.org/TR/2013/NOTE-prov-xml-20130430/
.. _The PROV-JSON Serialization: https://www.w3.org/submissions/prov-json/
.. _The PROV Ontology: https://www.w3.org/TR/2013/REC-prov-o-20130430/
