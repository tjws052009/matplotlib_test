Optional scikit-learn dependency for the learning bench
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ml_studio`` fits models with scikit-learn >= 1.4. The pin is recorded in:

- the ``ml`` dependency group in ``pyproject.toml``
- ``environment.yml``
- the optional dependencies in :ref:`dependencies`
- ``ml_studio/requirements.txt``

scikit-learn is not required to import Matplotlib. It is intentionally absent
from ``[project] dependencies``, the ``build`` dependency group,
``[build-system] requires``, ``ci/minver-requirements.txt``, and
``matplotlib._check_versions``. Those lists are the install and the minimum
version of Matplotlib itself. The bench is a separate tool in the checkout.
