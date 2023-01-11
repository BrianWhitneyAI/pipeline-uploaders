# -*- coding: utf-8 -*-

from .celigo_uploader import CeligoUploader
from .emt_uploader import EMTUploader

# from .drug_uploader import DrugUploader
from .fms_uploader import FMSUploader

"""Top-level package for pipeline_uploaders."""

__author__ = "Brian Whitney"
__email__ = "brian.whitney@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "1.1.0"


def get_module_version():
    return __version__
