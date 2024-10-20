import site

from setuptools import setup


setup(
    name="bf",
    version="0.1.0",
    description="",
    python_requires="== 2.7.18",
    install_requires=[],
    extras_require={
        "dev": [],
    },
    data_files=[(site.USER_SITE, "pypy.pth")]
)
