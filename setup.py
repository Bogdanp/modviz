from setuptools import setup

setup(
    name="modviz",
    version="0.2.0",
    description="Modviz lets you visualize your module dependencies.",
    long_description="https://github.com/Bogdanp/modviz",
    packages=["modviz"],
    install_requires=[],
    include_package_data=True,
    entry_points=dict(console_scripts=["modviz = modviz.cli:main"]),
    author="Bogdan Popa",
    author_email="popa.bogdanp@gmail.com",
    url="https://github.com/Bogdanp/modviz",
    keywords=["visualization"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
    ]
)
