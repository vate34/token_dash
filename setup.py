"""py2app setup script for Token Dashboard."""

import zlib
import os
import subprocess
import sys

# Fix for Python 3.12+ where zlib is built-in and lacks __file__
if not hasattr(zlib, "__file__"):
    zlib.__file__ = __file__

# Generate icon if not present
_icon_path = os.path.join(os.path.dirname(__file__), "assets", "app.icns")
if not os.path.exists(_icon_path):
    subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "scripts", "make_icon.py")],
        check=True,
    )

from setuptools import setup

APP = ["runner.py"]
DATA_FILES: list[str] = []
OPTIONS = {
    "argv_emulation": False,
    "plist": {
        "LSUIElement": True,
        "CFBundleName": "Token Dash",
        "CFBundleDisplayName": "Token Dashboard",
        "CFBundleIdentifier": "com.token-dash.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "NSHighResolutionCapable": True,
        "CFBundleIconFile": "app.icns",
    },
    "resources": [("", ["assets/app.icns"])],
    "packages": ["token_dash", "Foundation", "AppKit", "WebKit", "Quartz", "CoreFoundation", "objc"],
    "includes": [
        "Foundation", "AppKit", "WebKit", "Quartz", "CoreFoundation", "objc",
        "PyObjCTools.KeyValueCoding",
    ],
}

kwargs: dict = {}
try:
    from py2app.build_app import py2app as _py2app

    class Py2App(_py2app):
        def finalize_options(self):
            self.distribution.install_requires = None
            super().finalize_options()

    kwargs["cmdclass"] = {"py2app": Py2App}
except ImportError:
    pass

setup(
    name="Token Dash",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    **kwargs,
)
