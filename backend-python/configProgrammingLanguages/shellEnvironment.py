from settings import copyFilesAndClose


def createShellEnvironment(myProjectFolder, linuxVersion):
    file = open(myProjectFolder + "/Dockerfile", "a")

    if linuxVersion is not None:
        my_linuxVersion = linuxVersion
    else:
        my_linuxVersion = "18.04"
        my_linuxVersion = "20.04"
        my_linuxVersion = "22.04"

        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update\n")
        file.write("RUN apt upgrade -y\n")

    copyFilesAndClose(file, linuxVersion)
    return my_linuxVersion
