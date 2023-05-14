from setuptools import setup
#from setuptools import find_packages

with open("README.md") as f_readme:
    long_description = f_readme.read()

setup(
    name='durdraw',
    version='0.19.2',
    author='Sam Foster',
    author_email='samfoster@gmail.com',
    description='Animated Color ASCII and Unicode Art Editor',
    long_description = long_description,
    #py_modules=["PyGObject"],
    url='https://github.com/cmang/durdraw',
    license='ISC',
    # package_dir={'': 'durdraw'},
    packages=['durdraw'],
    install_requires=['pillow', 'windows-curses;platform_system=="Windows"'],
    include_package_data = True, 
    package_data = {'durdraw': ["help/*"]}, # help/durhelp.dur
    data_files = [
    #    ('share/icons', ['data/durdraw.png']),
    #    ('share/applications', ['data/durdraw.desktop']),
    #    ('share/durdraw', ['examples/*.dur']),
        ('share/durdraw', ['examples/cm-doge.asc']),
        ('share/durdraw', ['examples/cm-doge.dur']),
        ('share/durdraw', ['examples/eye.dur']),
        ('share/durdraw', ['examples/mane.dur']),
        ('share/durdraw', ['examples/rain.dur']),
    ],
    classifiers=[
        'Environment :: Console :: Curses',
        'Topic :: Artistic Software',
        'Topic :: Text Editors',
        'Topic :: Terminals',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities'
    ],
    entry_points={
    'console_scripts': [
        'durdraw = durdraw.main:main',
    ],
},
)

