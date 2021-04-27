import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='tbpp_cf2',
    version='0.0.1',
    author='Nico Strasdat',
    author_email='nstrasdat@gmail.com',
    description='Compact Models for the Temporal Bin Packing Problem with Fire-Ups',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/wotzlaff/tbpp-cf2',
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires='>=3.9',
)
