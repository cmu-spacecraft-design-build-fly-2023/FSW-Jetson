#!/usr/bin/env python3


from setuptools import setup, find_packages


# Read package description
with open("README.md", "r") as f:
    long_description = f.read()


# Read common requirements
requirements = []
with open("requirements.txt") as fp:
    for line in fp:
        requirements.append(line.strip())


setup(
    name="FSW-Jetson",
    version="0.0.0",
    packages=find_packages(),
    description="Flight Software the the Payload of Argus-1.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmu-spacecraft-design-build-fly-2023/FSW-Jetson",
    license="MIT",
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.8.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
