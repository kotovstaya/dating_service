from setuptools import find_packages, setup


def load_requirements(fname: str):
    with open(fname) as f:
        line_iter = (line.strip() for line in f.readlines())
        return [line for line in line_iter if line and line[0] != '#']


setup(
    name="dating_llm",
    version="0.0.1",
    author="Anton Savinkov",
    author_email="antsavinkov@gmail.com",
    description="dating llm service",
    license="MIT",
    long_description_content_type="text/markdown",
    platforms="all",
    python_requires=">=3.10",
    packages=find_packages(include=['dating_llm', 'dating_llm.*'], exclude=["tests"]),
    include_package_data=True,
)
