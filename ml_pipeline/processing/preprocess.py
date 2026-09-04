"""
Resume text preprocessing — delegates to the shared implementation
in backend/shared_preprocessing.py so training and inference are
always identical.  Preserves the ``clean_resume`` name for
backward-compatibility with train_model.py / predict.py.
"""

import sys
import os

# Ensure the backend package is importable when running from ml_pipeline/
_backend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
if _backend_dir not in sys.path:
    sys.path.insert(0, os.path.abspath(_backend_dir))

from shared_preprocessing import clean_resume_text as clean_resume  # noqa: F401
