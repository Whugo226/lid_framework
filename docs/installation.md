# Installation

The framework is not published on PyPI; install it from source. See the README
for the conda route, which recreates the environment used for the thesis.

## From source

The source files can be downloaded from the [GitHub repo](https://github.com/Whugo226/lid_framework). The repository is named `lid_framework`; the Python package it installs is `lid_toolkit`.

You can either clone the public repository:

```sh
git clone https://github.com/Whugo226/lid_framework.git
```

Or download the [tarball](https://github.com/Whugo226/lid_framework/tarball/main):

```sh
curl -OJL https://github.com/Whugo226/lid_framework/tarball/main
```

Once you have a copy of the source, you can install it with:

```sh
cd lid_framework
pip install ".[spacy-models]"
```
