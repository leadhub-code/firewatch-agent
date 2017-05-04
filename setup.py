import re
from setuptools import setup, find_packages


def get_version():
    with open('firewatch_agent/main.py') as f:
        for line in f:
            m = re.match(r'''^version = ['"]([^'"]+)['"]$''', line)
            if m:
                return m.group(1)
    raise Exception('Failed to find version info')


version = get_version()


setup(
    name='firewatch-agent',
    version=version,
    description='Log monitoring for error and warning messages',
    url='https://github.com/leadhub-code/firewatch-agent',
    author='Petr Messner',
    author_email='petr.messner@gmail.com',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        #'Intended Audience :: Developers',
        #'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='log monitoring errors warnings',
    packages=find_packages(exclude=['doc*', 'test*']),
    install_requires=[
        'requests',
        'pyyaml',
    ],
    extras_require={
        #'dev': ['check-manifest'],
        #'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'firewatch-agent=firewatch_agent:agent_main',
        ],
    },
)
