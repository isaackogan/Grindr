import setuptools

# PyPi upload Command
# rm -r dist ; python setup.py sdist ; python -m twine upload dist/*

manifest: dict = {
    "name": "Grindr",
    "license": "MIT",
    "author": "Isaac Kogan",
    "version": "0.2.0.post3",
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
            'Grindr.client.web.tls_patch': ['ja3_blueprint.json', 'openssl.cnf'],
        },
        author=manifest["author"],
        author_email=manifest["email"],
        url="https://github.com/isaackogan/Grindr",
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords=["Grindr", "Grindr API", "python3", "api", "unofficial"],
        install_requires=[
            "pyee==12.1.1",
            "httpx==0.28.1",
            "pygeohash==1.2.0",
            "pydantic",
            "websockets_proxy==0.1.3",
        ],
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Topic :: Software Development :: Build Tools",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
        ]
    )
