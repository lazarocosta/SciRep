from settings import copyFilesAndClose


def rEnvironment_windows(myProjectFolder, rVersionString, windowsVersion):
    file = open(myProjectFolder + "/Dockerfile", "a")
    rVersion = rVersionString.split("R:")[1]
    ## ["R:4.3.1", "R:4.3.0", "R:4.2.3", "R:4.2.2", "R:4.2.0", "R:4.0.0", "R:3.6.0"]
    allowRVersion = ["4.3.1", "4.3.0", "4.2.3", "4.2.2", "4.2.0", "4.0.0", "3.6.0"]

    if rVersion not in allowRVersion:
        file.close()
        raise ValueError("R version is not available")

    if windowsVersion is not None:
        my_linuxVersion = windowsVersion
    else:
        my_linuxVersion = True

        file.write("# Use the Windows Server Core image as the base image\n")
        file.write("FROM mcr.microsoft.com/windows/servercore:ltsc2019\n")

    file.write("ENV R_VERSION " + rVersion + "\n")
    file.write("# Download and install Microsoft R Open\n")
    file.write("ADD https://cran.r-project.org/bin/windows/base/old/${R_VERSION}/R-${R_VERSION}-win.exe C:/R-win.exe\n")

    file.write("# Install R silently\n")
    file.write("RUN C:\R-win.exe /SILENT\n")
    file.write('''RUN powershell -Command "Remove-Item -Path 'c:\R-win.exe'"\n''')

    file.write("# Add R to the PATH\n")
    file.write('RUN setx /M PATH "%PATH%;C:\Program Files\R\R-%R_VERSION%\\bin\\x64"\n')

    copyFilesAndClose(file, windowsVersion)

    return my_linuxVersion


def rEnvironment_linux(myProjectFolder, rVersionString, linuxVersion):
    file = open(myProjectFolder + "/Dockerfile", "a")
    rVersion = rVersionString.split("R:")[1]
    allowRVersion = ["4.3.1", "4.3.0", "4.2.3", "4.2.2", "4.2.0", "4.0.0", "3.6.0"]

    if rVersion not in allowRVersion:
        file.close()
        raise ValueError("R version is not available")

    if linuxVersion is not None:
        my_linuxVersion = linuxVersion
    else:
        my_linuxVersion = "22.04"
        my_linuxVersion = "20.04"
        my_linuxVersion = "18.04"

        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update\n")
        file.write("RUN apt upgrade -y\n")

    # file.write("RUN apt install dirmngr gnupg apt-transport-https ca-certificates software-properties-common -y\n")
    # file.write("RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9\n")
    # file.write("RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'\n")
    file.write("RUN apt install r-base -y\n")
    file.write("RUN apt install build-essential -y\n")

    copyFilesAndClose(file, linuxVersion)

    return my_linuxVersion

#################--------------------
# FROM ubuntu:18.04
# RUN apt update
# RUN apt upgrade -y
##RUN add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'
# RUN apt install r-base -y
# RUN apt install build-essential -y

# WORKDIR /files
# COPY ./files .

# RUN R -e "install.packages('stringr')"


#################--------------------
# FROM rocker/r-base:latest
# WORKDIR /files
# COPY ./files .
# RUN Rscript CODE/00_Startup.R
# demorou 15min

#################--------------------


##CMD Rscript myfile.R


# docker build -t e593eeca-2e65-4ee9-b997-5e88b5020ca9:111 .
# docker container run  -it e593eeca-2e65-4ee9-b997-5e88b5020ca9:111 /bin/bash


# Rscript.exe pathToFile.R


#
# User
# there are some command that done the some functionality that "pipreqs" but in R language
#
# ChatGPT
# Yes, there are some R packages that provide similar functionality to pipreqs, which generates a list of required Python packages based on the import statements in a Python project. Here are a few R packages that you can use to generate a list of required R packages based on the function calls in an R project:
#
# packrat: This package provides a complete dependency management system for R projects, including package installation, version control, and project isolation. You can use the packrat::init() function to create a new project with a package library, and the packrat::snapshot() function to generate a snapshot of the package dependencies for the project.
#
# renv: This package provides a lightweight and reproducible dependency management system for R projects. You can use the renv::init() function to create a new project with a package library, and the renv::snapshot() function to generate a snapshot of the package dependencies for the project.
#
# dependencies: This package provides a set of functions for analyzing and visualizing package dependencies in R projects. You can use the dependencies::package_deps() function to generate a list of required packages based on the function calls in an R script or package.
#
# packrat::bundle: This function generates a compressed bundle of all the package dependencies required by the R project. You can use this function to share your project and its dependencies with others.
#
# Note that these packages may have different functionality and usage than pipreqs, so it's important to read the documentation and choose the package that best fits your needs.
