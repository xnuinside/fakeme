import os

import pytest


def LOCAL_ONLY(*args, **kwargs):
    return pytest.mark.skipif(os.environ.get("ENV") == "ci", reason="only local")(
        *args, **kwargs
    )
