=========================
``ttree`` — taxonomy tree
=========================

|Build Status| |Documentation Status| |License|

Taxonomy tree implementation.

`Tree data structure
<http://en.wikipedia.org/wiki/Tree_%28data_structure%29>`_ is an
important data structure in computer programming languages. It has
wide applications with hierarchical data connections say file systems
and some algorithms in Machine Learning. `ttree
<https://github.com/vovanbo/ttree>`_ is created to provide an
efficient implementation of tree data structure in Python.

The main features of ``ttree`` includes:

    * Efficient operation of node indexing with the benefit of dictionary type.
    * Support common tree operations like **traversing**, **insertion**,
      **deletion**, **node moving**, **shallow/deep copying**,
      **subtree cutting** etc.
    * Support user-defined data payload to accelerate your model construction.
    * Has pretty tree showing and text/json dump for pretty print and offline
      analysis.

Quick Start
-----------

.. code:: bash

    $ pip install ttree

Documentation
-------------

For installation, APIs and examples, see http://ttree.readthedocs.io/en/latest/

Update
------

-  2017-12-06: Fork ``treelib`` to ``ttree`` package by `Vladimir Bolshakov`_
-  2017-08-10: Abandon supporting Python 3.2 since v1.4.0.
-  2012-07-07: First published.

Contributors
------------

-  `Brett Alistair Kromkamp <brettkromkamp@gmail.com>`_
    Post basic idea online.
-  `Xiaming Chen <chenxm35@gmail.com>`_
    Finished primary parts and made the library freely public.
-  `Holger Bast <holgerbast@gmx.de>`_
    Replaced list with ``dict`` for fast node index and optimized
    the performance.
-  `Ilya Kuprik <ilya-spy@ynadex.ru>`_
    Added ZIGZAG tree-walk algorithm to tree traversal.
-  `Vladimir Bolshakov`_
    Performance improvements, add typings, drop Python 2 support

.. _Vladimir Bolshakov: https://github.com/vovanbo

.. |Build Status| image:: https://travis-ci.org/vovanbo/ttree.svg?branch=master
   :target: https://travis-ci.org/vovanbo/ttree
.. |Documentation Status| image:: https://readthedocs.org/projects/ttree/badge/?version=latest
   :target: http://ttree.readthedocs.io/en/latest/?badge=latest
.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0
