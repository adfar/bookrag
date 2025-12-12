from setuptools import setup, find_packages

setup(
    name="bookrag",
    version="0.1.0",
    description="Convert markdown manuscripts into interactive web books with AI chat",
    author="Your Name",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
        "PyYAML>=6.0",
        "Jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "bookrag=bookrag.cli:cli",
        ],
    },
    python_requires=">=3.8",
)
