"""py2app setup script for Token Dashboard."""

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
    },
    "packages": ["token_dash", "Foundation", "AppKit", "WebKit", "Quartz", "CoreFoundation", "objc", "PyObjCTools"],
    "includes": [
        "Foundation", "AppKit", "WebKit", "Quartz", "CoreFoundation", "objc",
        "PyObjCTools.KeyValueCoding",
    ],
    "resources": [
        (".", ["token_dash/.venv/lib/python3.9/site-packages/PyObjCTools"]),
    ],
}

setup(
    name="Token Dash",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
