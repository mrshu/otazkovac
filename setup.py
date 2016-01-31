from setuptools import setup

setup(
    name='otazkovac',

    description='Question generator for Slovak language',
    author='Marek Suppa',
    author_email='marek@suppa.sk',
    version='0.0.3',

    url='https://github.com/mrshu/otazkovac',

    include_package_data=True,
    setup_requires=['numpy'],
    install_requires=['numpy', 'scipy', 'sklearn', 'ufal.morphodita', 'Click',
                      'Flask'],
    packages=['otazkovac'],

    license="GPL 3.0",
    keywords=['question', 'generation', 'nlp'],
    entry_points={
        'console_scripts': [
            'otazkovac = otazkovac:main'
        ]
    }
)
