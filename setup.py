from setuptools import setup #type: ignore

setup(
    name="ga4py",
    version="1.0.0",
    description="Python package to simplify adding GA4 tracking to Python functions",
    author="Aira Innovations",
    packages=["gapy"],
    install_requires=[
        "ga4mp==2.0.4",
        "requests==2.25.1",
        "google-api-python-client==2.5.0",
        "google-auth==1.30.0",
        "google-auth-httplib2==0.1.0",
        "google-auth-oauthlib==0.4.4"
    ],
)
