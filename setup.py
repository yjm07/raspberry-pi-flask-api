from os import path
from io import open
from setuptools import setup, find_packages

def get_spec(filename: str, mode: str = 'r'):
    def wrapper():
        here = path.dirname(__file__)
        result = {}
        with open(path.join(here, filename), encoding='utf8') as src_file:
            if mode == 'd':
                exec(src_file.read(), result)
            else:
                result = src_file.read()
        return result
    return wrapper


get_about = get_spec('./berry/about.py', 'd')
get_requirements = get_spec('requirements.txt')

about = get_about()
setup(
    name=about['__title__'],
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__email__'],
    packages=find_packages(),
    install_requires=get_requirements()
)
