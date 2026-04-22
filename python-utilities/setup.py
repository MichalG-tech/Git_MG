"""
Power BI Semantic Model Utilities
Professional automation toolkit for Power BI TMDL management
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="powerbi-utilities",
    version="1.0.0",
    description="Professional automation toolkit for Power BI semantic models",
    author="Michal Glanowski",
    author_email="michal@example.com",
    url="https://github.com/MichalG-tech/Git_MG",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=requirements,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "pb-validate=validators.tmdl_validator:main",
        ],
    },
)
