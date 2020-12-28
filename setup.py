"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['numpy', 'datetime', 'python-dateutil', 
    'scipy>=1.4.1', 'matplotlib']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest>=3']

setup(
    author="Xu Ren",
    author_email='xuren2120@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Fixed income related calculation in Python",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n',
    include_package_data=True,
    keywords='fincomepy',
    name='fincomepy',
    packages=find_packages(include=['fincomepy', 'fincomepy.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/reese3928/fincomepy',
    version='0.1.0',
    zip_safe=False,
)
