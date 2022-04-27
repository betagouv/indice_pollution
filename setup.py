from setuptools import find_packages, setup


def get_version():
    from setuptools_scm import get_version
    return get_version()

if __name__ == '__main__':
    setup(
        version=get_version()
    )

