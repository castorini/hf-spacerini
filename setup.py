import setuptools

with open('README.md') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='spacerini',
    version='0.0.0',
    packages=setuptools.find_packages(),
    url='https://github.com/castorini/hf-spacerini',
    license='MIT',
    author='',
    author_email='',
    description='',
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
