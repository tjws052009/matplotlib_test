Learning bench for scikit-learn
-------------------------------

A checkout can now serve a local page that fits a scikit-learn model on a
background worker and draws the scores, confusion matrix, residuals, and a
two-dimensional view with Matplotlib. Set the dataset, estimator, and
parameters in the page; the request returns as soon as the job is queued.

From the repository root::

    pip install -r ml_studio/requirements.txt
    python -m ml_studio

The page listens on http://127.0.0.1:47321. scikit-learn >= 1.4 is required
to run the bench. Importing Matplotlib does not import scikit-learn.
