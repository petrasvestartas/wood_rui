from setuptools import setup, find_packages

setup(
    name="wood_rui",  # Name of the package
    version="0.1.0",  # Version of the package
    description="A package for managing wood joinery geometries in Rhino8.",
    long_description=open("README.md").read(),  # Long description from README file
    long_description_content_type="text/markdown",
    author="Petras Vestartas",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/wood_rui",  # URL of the project (e.g., GitHub)
    packages=find_packages(),  # Automatically find package directories
    include_package_data=True,  # Include data files specified in MANIFEST.in
    install_requires=[],  # List dependencies here or read from requirements.txt
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9.10",  # Specify minimum Python version
)
