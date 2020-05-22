from setuptools import setup, find_packages

setup(
    name="git_split_commit",
    packages=find_packages(),
    version="0.1.0",
    install_requires=["click", "coloredlogs", "gitpython", "simple-term-menu"],
    entry_points={"console_scripts": ["git-split-commit = git_split_commit.command:split"]},
)
