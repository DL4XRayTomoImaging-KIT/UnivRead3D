import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open('requirements.txt') as file:
    reqs = file.readlines()
    reqs = [line.rstrip() for line in lines]

setuptools.setup(
    name='univ_read',
    version='0.0.1',
    author='Jwalin Bhatt',
    author_email='jwalin.bhatt@gmail.com',
    description='Universal 3D file reader',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/DL4XRayTomoImaging-KIT/UnivRead3D',
    packages=setuptools.find_packages(),
    install_requires=reqs,
)