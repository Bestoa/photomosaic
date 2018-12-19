from setuptools import setup, find_packages
import photomosaic

setup(
    name = 'photomosaic',
    version = photomosaic.__VERSION__,
    author = 'Besto',
    author_email = 'bestoapache@gmail.com',
    license = 'AGPL',
    packages = find_packages(),
    install_requires = ['Pillow', 'numpy', 'cachetools'],
)

