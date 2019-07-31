from setuptools import setup, find_packages


setup(
        name='turo-parser',
        version='1.0.0',
        description="Apache Log Parser CLI",
        author="Jacob Alheid",
        author_email="shakefu@gmail.com",
        packages=find_packages(exclude=['test']),
        install_requires=[
            'apache-log-parser',
            'configargparse',
            'pytool',
            ],
        entry_points={
            'console_scripts': [
                'turo-parser=turo_parser.main:Main.console_script',
            ],
        },
        test_suite='nose.collector',
        tests_require=[
            'nose',
            ],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.7',
            'Topic :: Utilities',
            ]
        )

