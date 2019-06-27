import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sdc_api",
    version="0.2.1",
    author="Tomori Project",
    author_email="dev@discord.band",
    description="An async wrapper for Server-Discord.Com API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TomoriBot/sdc_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)