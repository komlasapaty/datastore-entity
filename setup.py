import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="datastore-entity",
    version="0.2.0",
    author="Seyram Komla Sapaty",
    author_email="komlasapaty@gmail.com",
    description="A simple ORM-like interface to Google Cloud NoSQL Datastore",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/komlasapaty/datastore-entity",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires='>=3.5',
    install_requires=[
        'google-cloud-datastore>=1',
        ]
)