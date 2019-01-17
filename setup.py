from setuptools import setup

options = {"name" : "pythonjit",
           "version" : "1.1.1",
           "description" : "Automatically cross compiles python to C",
           #"long_description" : '',
           #"url" : "",
           #"download_url" : "",
           "author" : "Ella Rose",
           "author_email" : "python_pride@protonmail.com",
           "packages" : ["pythonjit"],
           "classifiers" : ["Development Status :: 4 - Beta",
                            "Intended Audience :: Developers",
                            "License :: OSI Approved :: MIT License",
                            "Operating System :: Microsoft :: Windows",
                            "Operating System :: POSIX :: Linux",
                            "Programming Language :: Python :: 2.7",
                            "Topic :: Software Development :: Libraries :: Python Modules"]
                            }

if __name__ == "__main__":
    setup(**options)
