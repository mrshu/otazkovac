from setuptools import setup

setup(
    name='otazkovac',

    description='Question generator for Slovak language',
    author='Marek Suppa',
    author_email='marek@suppa.sk',
    version='0.0.1',

    url='https://github.com/mrshu/otazkovac',

    include_package_data=True,
    install_requires=['sklearn', 'ufal.morphodita'],
    packages=['otazkovac'],

    license="GPL 3.0",
    keywords=['question', 'generation', 'nlp'],
    entry_points={
        'console_scripts': [
            'otazkovac = otazkovac:main'
        ]
    }
)
