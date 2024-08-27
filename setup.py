from setuptools import setup  # type: ignore

setup(
    name="ga4py",
    version="1.1.0",
    description="Python package to simplify adding GA4 tracking to Python functions",
    author="Aira Innovations",
    packages=["ga4py"],
    install_requires=[
        "ga4mp==2.0.4",
        "requests==2.32.3",
    ],
    package_data={"ga4py": ["py.typed"]},
)
