# -*- coding: utf-8 -*-

"""Top-level package for pipeline_uploaders."""

__author__ = "Brian Whitney"
__email__ = "brian.whitney@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.0"


def get_module_version():
    return __version__


from .example import Example  # noqa: F401
from .fms_uploader import FMSUploader
from .celigo_uploader import CeligoUploader
from .drug_uploader import DrugUploader