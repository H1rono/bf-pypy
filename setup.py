from distutils import sysconfig

from setuptools import setup


site_packages_path = sysconfig.get_python_lib()

setup(
    name="bf",
    version="0.1.0",
    description="",
    python_requires="== 2.7.18",
    install_requires=[],
    extras_require={
        "dev": [],
    },
    data_files=[]
)
