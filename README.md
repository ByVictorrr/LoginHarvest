# LoginHarvest
An API to get you the xpath of common needs to login to the website like oauth button, or navigation button. It also includes input like for username and password.

## Install the Package Locally (Optional)
To install your package locally for testing, run the following command in your terminal:
```sh
pip install -e .
```

##  Build the Package
To build your package for PyPI, use the following commands:
```shell
python setup.py sdist bdist_wheel
```

## Upload to PyPI
Make sure you have an account on PyPI. To upload the package to PyPI, use Twine:

```sh
pip install twine
twine upload dist/*
```

## Use the Package
Now that your package is uploaded, you can install it using pip:

```sh
pip install html-extractor
```