from setuptools import setup
from ghi import __version__


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name="ghi",
    version=__version__,
    description="GitHub IRC Notification Service",
    long_description=readme(),
    author="Graham Krizek",
    author_email="graham@krizek.io",
    url="https://github.com/gkrizek/ghi",
    install_requires=[
        "PyYAML",
        "requests",
        "tornado"
    ]
)
