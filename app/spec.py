import yaml
import os

from .config import SPEC_DIR, DISABLE_SECURITY

with open(os.path.join(SPEC_DIR, "openapi.yaml"), "r") as f:
    openapi_spec = yaml.full_load(f)

if DISABLE_SECURITY:
    openapi_spec.pop("security", None)

    for path in openapi_spec.get("paths", {}).values():
        for method in path.values():
            method.pop("security", None)
