import setuptools

with open('requirements.txt') as file:
    reqs = file.readlines()
    reqs = [req.rstrip() for req in reqs]

setuptools.setup(
    name='univread',
    version='0.0.2',
    author='Jwalin Bhatt',
    author_email='jwalin.bhatt@gmail.com',
    description='Universal 3D file reader',
    url='https://github.com/DL4XRayTomoImaging-KIT/UnivRead3D',
    packages=setuptools.find_packages(),
    install_requires=reqs,
)