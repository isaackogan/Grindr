import setuptools

# PyPi upload Command
# rm -r dist ; python setup.py sdist ; python -m twine upload dist/*

manifest: dict = {
    "name": "Grindr",
    "license": "MIT",
    "author": "Isaac Kogan",
    "version": "0.2.2.post1",
    "email": "info@isaackogan.com"
}

if __name__ == '__main__':
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

    setuptools.setup(
        name=manifest["name"],
        packages=setuptools.find_packages(),
        version=manifest["version"],
        license=manifest["license"],
        description="Grindr Python Client",
        include_package_data=True,  # Ensure non-Python files are included
        package_data={
            'Grindr.client.web.tls_match': ['ja3_blueprint.json'],
        },
        author=manifest["author"],
        author_email=manifest["email"],
        url="https://github.com/isaackogan/Grindr",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=["Grindr", "Grindr API", "python3", "api", "unofficial"],
        install_requires=[
            "pyee==12.1.1",
            "pygeohash==1.2.0",
            "pydantic",
            "curl_cffi==0.8.1b8"
        ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Build Tools",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Programming Language :: Python :: 3.12",
            "Framework :: Pydantic :: 2"
        ]
    )
