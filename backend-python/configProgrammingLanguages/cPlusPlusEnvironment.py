from settings import copyFiles


def createCPlusPlusEnvironment_linux(myProjectFolder, gccVersionString, linuxVersion):
    ##["gcc:12.1", "gcc:11.3", "gcc:10.3", "gcc:9.4", "gcc:8.4", "gcc:7.5"]
    # FROM ubuntu:22.04 =versao (entre 9 e 12) deu aqui gcc
    # FROM ubuntu:20.04 =versao (entre 7 e 11 inclusive) deu aqui gcc adicionando isto ppa:ubuntu-toolchain-r/test -y
    # FROM ubuntu:18.04 =versao (entre 7 e 11 inclusive) deu aqui gcc adicionando isto ppa:ubuntu-toolchain-r/test -y

    file = open(myProjectFolder + "/Dockerfile", "a")

    #allowgccVersion = [12.1, 11.3, 10.3, 9.4, 8.4,7.5]
    allowgccVersion = [12, 11, 10, 9, 8, 7]

    gccVersion = gccVersionString.split("gcc:")[1]

    if int(gccVersion) not in allowgccVersion:
        file.close()
        raise Exception("Gcc version is not available")

    if linuxVersion is None:
        if int(gccVersion) >= 12:
            my_linuxVersion = "22.04"
        elif int(gccVersion) < 9:
            my_linuxVersion = "20.04"
            my_linuxVersion = "18.04"
        else:
            my_linuxVersion = "18.04"
            my_linuxVersion = "20.04"
            my_linuxVersion = "22.04"

        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update\n")
        file.write("RUN apt upgrade -y\n")
    else:
        my_linuxVersion = linuxVersion



    file.write("RUN apt install -y software-properties-common\n")
    file.write("RUN add-apt-repository ppa:ubuntu-toolchain-r/test -y\n")
    file.write("RUN apt update\n")

    file.write("RUN apt install -y gcc-" + gccVersion + "\n")
    file.write("RUN apt install -y make \n")
    file.write("RUN apt install -y g++" + gccVersion + "\n")
    file.write(
        "RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-" + gccVersion + " 2000 --slave /usr/bin/g++ g++ /usr/bin/g++-" + gccVersion + "\n\n")

    copyFiles(file, linuxVersion)

    file.write("RUN make\n")
    file.close()
    return my_linuxVersion

def createCPlusPlusEnvironment_windows(myProjectFolder, gccVersionString, windowsVersion):
    ##["gcc:12.1", "gcc:11.3", "gcc:10.3", "gcc:9.4", "gcc:8.4", "gcc:7.5"]
    # FROM ubuntu:22.04 =versao (entre 9 e 12) deu aqui gcc
    # FROM ubuntu:20.04 =versao (entre 7 e 11 inclusive) deu aqui gcc adicionando isto ppa:ubuntu-toolchain-r/test -y
    # FROM ubuntu:18.04 =versao (entre 7 e 11 inclusive) deu aqui gcc adicionando isto ppa:ubuntu-toolchain-r/test -y

    file = open(myProjectFolder + "/Dockerfile", "a")

    # allowgccVersion = [12.1, 11.3, 10.3, 9.4, 8.4,7.5]
    allowgccVersion = [12, 11, 10, 9, 8, 7]

    gccVersion = gccVersionString.split("gcc:")[1]

    if int(gccVersion) not in allowgccVersion:
        file.close()
        raise Exception("Gcc version is not available")

    if windowsVersion is None:
        if int(gccVersion) >= 12:
            my_linuxVersion = "22.04"
        elif int(gccVersion) < 9:
            my_linuxVersion = "20.04"
            my_linuxVersion = "18.04"
        else:
            my_linuxVersion = "18.04"
            my_linuxVersion = "20.04"
            my_linuxVersion = "22.04"

        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update\n")
        file.write("RUN apt upgrade -y\n")
    else:
        my_linuxVersion = windowsVersion

    file.write("RUN apt install -y software-properties-common\n")
    file.write("RUN add-apt-repository ppa:ubuntu-toolchain-r/test -y\n")
    file.write("RUN apt update\n")

    file.write("RUN apt install -y gcc-" + gccVersion + "\n")
    file.write("RUN apt install -y make \n")
    file.write("RUN apt install -y g++" + gccVersion + "\n")
    file.write(
        "RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-" + gccVersion + " 2000 --slave /usr/bin/g++ g++ /usr/bin/g++-" + gccVersion + "\n\n")

    copyFiles(file, windowsVersion)

    file.write("RUN make\n")
    file.close()
    return my_linuxVersion

    ##GCC
    # RUN  apt update &&  apt upgrade -y
    # RUN apt install -y gcc-12 make g++
    # RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 2000

    # frolvlad/alpine-gxx" -> apenas suporta "g++ -O3 ./src/bbfs_node.cpp -o out"
    # gcc:latest ->suporta fazer "make"


    ##GCC
    # RUN  apt update &&  apt upgrade -y
    # RUN apt install -y gcc-12 make g++
    # RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-12 2000

    # frolvlad/alpine-gxx" -> apenas suporta "g++ -O3 ./src/bbfs_node.cpp -o out"
    # gcc:latest ->suporta fazer "make"
