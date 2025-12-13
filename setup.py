from setuptools import setup, find_packages

setup(
    name="flwr-k8s-deploy",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "flwr_k8s_deploy": ["templates/*"],
    },
)
