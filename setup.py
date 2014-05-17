from setuptools import setup, find_packages

setup(
    name='emma',
    version=1.02,
    description='Image Databank for Django',
    long_description=open('README.rst').read(),
    author='Geert Dekkers',
    author_email='geert@djangowebstudio.nl',
    license='BSD',
    url='https://https://github.com/djangowebstudio/emma',
    packages=find_packages(exclude=['tests', 'tests.*']),
    platforms='any',
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia :: Graphics',
        'Framework :: Django',
    ]
)
