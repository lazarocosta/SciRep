import os
import re
import shutil
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
from stdlib_list import stdlib_list
import settingsPython
from model.model import getPythonFiles, getProjectFolders


def createPythonEnvironment_windows(myProjectFolder, hasRequirementsFile, pythonDependenciesToAddManually, pythonVersionString,
                            linuxVersion):
    # [ "python:3.11", "python:3.10", "python:3.9", "python:3.8","python:3.7",]
    # FROM ubuntu:22.04 >=3.10 deu aqui python [default 3.10]
    # FROM ubuntu:20.04 3.8;3.9 deu aqui python [default 3.8]
    # FROM ubuntu:18.04 <=3.8 deu aqui python [default 3.6]

    # RUN apt install -y python3.8
    # RUN apt install -y python3-pip

    # RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python3.8 2000
    # RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 2000

    allowPythonVersion = ["3.11", "3.10", "3.9", "3.8", "3.7"]
    pythonVersion = pythonVersionString.split("python:")[1]
    file = open(myProjectFolder + "/Dockerfile", "a")

    if pythonVersion not in allowPythonVersion:
        file.close()
        raise ValueError("Python version is not available")

    if linuxVersion is None:
        if float(pythonVersion) == 3.9:
            my_linuxVersion = "20.04"
        elif float(pythonVersion) == 3.10 or float(pythonVersion) == 3.11:
            my_linuxVersion = "22.04"
        else:
            my_linuxVersion = "18.04"
        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update && apt upgrade -y\n")
    else:
        my_linuxVersion = linuxVersion

    file.write('RUN apt install software-properties-common -y\n')
    file.write('RUN add-apt-repository ppa:deadsnakes/ppa -y\n')
    file.write('RUN apt update\n')

    file.write("RUN apt install -y python" + pythonVersion + "\n")
    file.write("RUN apt install -y python3-pip\n")

    file.write(
        "RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python" + pythonVersion + " 2000\n")
    file.write("RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 2000\n")

    # shutil.copy(os.getcwd() + "\\configProgrammingLanguages\\checkDependencies.py", projectFiles + "/checkDependencies.py")
    file.write('RUN pip install --upgrade pipreqs\n')
    ## jupyter notebook pipreqsnb
    ##https://pypi.org/project/pipreqsnb/
    ##https://medium.com/@ivalengy/pipreqsnb-pipreqs-with-jupyter-notebook-support-931dc3cf9330
    #pipreqsnb  .
    if linuxVersion is None:
        file.write("WORKDIR /files\n")
        # file.write("COPY ./requirements.txt .\n")
        file.write("COPY ./files .\n")

    #file.write('RUN pipreqs --ignore bin,etc,include,lib,lib64 --encoding utf-8 --savepath requirements.txt .\n')
    # file.write('RUN python checkDependencies.py\n')

    # file.write('RUN python -m pip install -r requirements.txt\n\n')

    if len(pythonDependenciesToAddManually) > 0:
        for library in pythonDependenciesToAddManually:
            file.write("RUN pip install " + library + "\n")

    file.write("\n")
    file.close()

    return my_linuxVersion


def validatePythonEnvironment(myProjectFolder,projectFiles, pythonDependencies):

    ##todo retirar
    # delete content from the Dockerfile
    open(projectFiles + "/requirements.txt", "w").close()
    with open(projectFiles + "/requirements.txt", 'w') as requirementsFile:
        for library in pythonDependencies:
            requirementsFile.write(library + "\n")
        requirementsFile.close()

    ##todo retirar
    # delete content from the Dockerfile
    open(myProjectFolder + "/Newdockerfile", "w").close()

    # open both files
    with open(myProjectFolder + "/Dockerfile", 'r') as Dockerfile, open(myProjectFolder + "/Newdockerfile", 'a') as myProjectFolder:

        # read content from first file
        for line in Dockerfile:
            # append content to second file
            myProjectFolder.write(line)

        myProjectFolder.write("RUN python -m pip install -r requirements.txt\n")

        # if len(pythonDependencies) > 0:
        #     for library in pythonDependencies:
        #         myProjectFolder.write("RUN pip install " + library + "\n")

        myProjectFolder.write("\n")
        myProjectFolder.close()
    return


def createPythonEnvironment_linux(myProjectFolder, projectFiles, hasRequirementsFile, projectUuid,
                             pythonDependenciesToAddManually, pythonVersionString, linuxVersion):
    libraryToInstall = []
    if not hasRequirementsFile:
        pythonFiles = getPythonFiles(projectUuid)
        projectFolders = getProjectFolders(projectUuid)

        pythonDependencies = pythonDependenciesToInstall(projectFiles, projectFiles, pythonFiles, projectFolders)
        # pythonDependencies= []
        print(pythonDependencies)
        # TODO alterar
        standardLibraries = stdlib_list("3.7")

        libraryToInstall = pythonDependenciesToInstallValidated(pythonDependencies, standardLibraries)

    try:
        pythonVersion = supportedPythonVersion(libraryToInstall)
    except Exception as e:
        print(str(e))
        raise ValueError(str(e))
    pythonVersion = re.findall('\d\.\d+', pythonVersion)[0]

    standardLibraries = stdlib_list(pythonVersion)

    file = open(myProjectFolder + "/Dockerfile", "a")
    # file.write("FROM python:" + pythonVersion + "\n\n")

    # [ "python:3.11", "python:3.10", "python:3.9", "python:3.8","python:3.7",]
    # FROM ubuntu:22.04 >=3.10 deu aqui python
    # FROM ubuntu:20.04 3.9 deu aqui python
    # FROM ubuntu:18.04 <=3.8 deu aqui python

    # RUN apt install -y python3.8
    # RUN apt install -y python3-pip

    # RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python3.8 2000
    # RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 2000

    if linuxVersion is not None:
        file.write("FROM ubuntu:" + linuxVersion + "\n")
        file.write("RUN apt update\n")
        file.write("RUN apt upgrade -y\n")
    # RUN apt install software-properties-common -y
    # RUN add-apt-repository ppa:deadsnakes/ppa -y
    # RUN apt update

    pythonVersion = pythonVersionString.split("python")[1]
    if pythonVersion in pythonVersionString:
        file.write("RUN apt install -y python" + pythonVersion + "\n")
        file.write("RUN apt install -y python3-pip\n")
    else:
        file.close()
        raise ValueError("Python version is not available")

    file.write(
        "RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python" + pythonVersion + " 2000\n")
    file.write("RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 2000\n")

    if linuxVersion is not None:
        file.write("WORKDIR /files\n")
        file.write("COPY ./files .\n\n")

    if hasRequirementsFile:
        file.write('RUN python -m pip install -r requirements.txt\n\n')
    else:
        libraryToInstall = set(libraryToInstall)
        for library in libraryToInstall:
            file.write("RUN pip install " + library + "\n")

    if len(pythonDependenciesToAddManually) > 0:
        for library in pythonDependenciesToAddManually:
            file.write("RUN pip install " + library + "\n")

    # if javaDockerImage:
    #     file.write('COPY --from=' + javaDockerImage['dockerImage'] + ' ' + javaDockerImage[
    #         'JAVA_HOME'] + ' /usr/local/my-java\n')
    #     file.write('ENV JAVA_HOME /usr/local/my-java\n')
    #     file.write('RUN update-alternatives --install /usr/bin/java java /usr/local/my-java/bin/java 2000\n\n')
    #     file.write('COPY --from=' + javaDockerImage['dockerImage'] + ' /usr/share/maven /usr/share/maven\n')
    #     file.write('ENV M2_HOME /usr/share/maven\n')
    #     file.write('ENV M2 $M2_HOME/bin\n')
    #     file.write('RUN update-alternatives --install /usr/bin/mvn mvn /usr/share/maven/bin/mvn 2000\n\n')
    #     file.write('RUN mvn clean package\n')

    file.write("\n")
    file.close()

    return


def pythonDependenciesToInstallValidated(pythonDependencies, standardLibraries):
    libraryToInstall = []
    for dependency in pythonDependencies:
        if not dependency in standardLibraries:
            with urlopen('https://pypi.org/search/?q=' + dependency) as r:
                text = r.read()
                soup = BeautifulSoup(text, "html.parser")
                # searchResults= soup.find_all(class_="package-snippet")
                searchResults = soup.find_all(class_="package-snippet__name")

                i = 0
                while i < 3 and i < len(searchResults):
                    indexResult = searchResults[i].contents[0]
                    i += 1
                    # TODO it is necessary to do it
                    if indexResult == "sklearn":
                        libraryToInstall.append("scikit-learn")
                        break
                    if indexResult == dependency:
                        libraryToInstall.append(indexResult)
                        # file.write("RUN pip install " + indexResult + "\n")
                        break

                    if i == 3:
                        libraryToInstall.append(searchResults[0].contents[0])
                        # file.write("RUN pip install " + searchResults[0].contents[0] + "\n")

                    # response = requests.get('https://pypi.org/pypi/pandas/json',  headers={"Accept":"application/json"})
                    # print(response.json().get("info").get("requires_dist"))
                    # print(response.json().get("info").get("requires_python"))
    return libraryToInstall


def pythonDependenciesToInstall(projectFiles, currentDirectory, pythonFiles, projectFolders):
    pythonDependencies = []

    for file in os.listdir(currentDirectory):
        # not an image and not a temporary file
        if os.path.isdir(currentDirectory + "/" + file):
            pythonDependencies += pythonDependenciesToInstall(projectFiles, currentDirectory + "/" + file, pythonFiles,
                                                              projectFolders)
        else:
            if not file.startswith('.') and file.endswith('.py') and os.path.isfile(currentDirectory + "/" + file):
                pythonDependencies += pythonDependenciesToInstallFromFile(projectFiles, currentDirectory, file,
                                                                          pythonFiles,
                                                                          projectFolders)

    pythonDependencies = [*set(pythonDependencies)]
    print("pythonDependencies:")
    print(pythonDependencies)
    return pythonDependencies


def pythonDependenciesToInstallFromFile(projectFiles, directory, file, pythonFiles,
                                        projectFolders):
    # TODO usar pythonFiles and projectFolders
    # print(os.access(file, os.R_OK))
    print("current Path:" + directory + "/" + file)

    fq = open(directory + "/" + file, "r", encoding="utf8")
    print(directory + "/" + file)
    try:
        fileRead = fq.read()
    except Exception as e:
        print(str(e))
        print("file:" + file)
        fq.close()
        return []
    pythonDependencies = []
    if fileRead == '':
        fq.close()
        return []
    if file == "rdc_based.py":
        print("ola")

    firstDependencies = [x.group() for x in
                         re.finditer(r'(?<!from)(?=(\t| )*)([a-z]|_|\.|[0-9])*(?=(\t| )* import ([a-z]|_|[0-9])*)',
                                     fileRead,
                                     flags=re.IGNORECASE | re.MULTILINE)]
    secondDependencies = [x.group() for x in
                          re.finditer(r'(?<=import )(?=(\t| )*)([a-z]|_|[0-9])*', fileRead,
                                      flags=re.IGNORECASE | re.MULTILINE)]
    firstDependencies = [dependencies.split('.')[0] for dependencies in firstDependencies]
    firstDependencies = [*set(firstDependencies)]
    firstDependenciesFinal = []

    if "" in firstDependencies:
        firstDependencies.remove('')

    for elemToSearch in firstDependencies:
        if not (os.path.exists(projectFiles + "/" + elemToSearch) or os.path.exists(
                directory + "/" + elemToSearch + ".py") or os.path.exists(
            directory + "/" + elemToSearch) or os.path.exists(directory + "/" + elemToSearch + ".py")):
            firstDependenciesFinal.append(elemToSearch)

    secondDependenciesFinal = []
    secondDependencies = [*set(secondDependencies)]

    if "" in secondDependencies:
        secondDependencies.remove('')

    for elemToSearch in secondDependencies:
        stringToSearch = "from (\s)*([a-z]|_|\.|[0-9])*(\s)* import (\s)*" + elemToSearch + "*(\s)*"
        result = re.search(stringToSearch, fileRead, re.IGNORECASE)
        if not (os.path.exists(projectFiles + "/" + elemToSearch) or os.path.exists(
                directory + "/" + elemToSearch + ".py") or result is not None):
            secondDependenciesFinal.append(elemToSearch)

    myPythonDependenciesAux = firstDependenciesFinal + secondDependenciesFinal
    print("filename:" + file)
    print("firstDependenciesFinal:")
    print(firstDependenciesFinal)
    print("secondDependenciesFinal:")
    print(secondDependenciesFinal)
    print("myPythonDependenciesAux")
    print(myPythonDependenciesAux)

    pythonDependencies += [dependencies.split('.')[0] for dependencies in myPythonDependenciesAux]

    # TODO verificar
    # https://pypi.org/search/?q=pandas
    # https://pypi.org/project/pandas/

    # with urlopen('https://pypi.org/project/pandas/') as r:
    #     text = r.read()
    #     soup = BeautifulSoup(text, "html.parser")
    #     pipCommand = soup.find(id="pip-command").contents[0]

    fq.close()
    print("-------------------------\n")
    return pythonDependencies


def supportedPythonVersion(libraryToInstallArray):
    ALL_PYTHON_VERSIONS = settingsPython.getAllPythonVersions()
    greaterThan = []
    lesserOrEqualThan = []
    lesserThan = []
    greaterOrEqualThan = []
    notPythonSupported = []

    for libraryToInstall in libraryToInstallArray:
        response = requests.get('https://pypi.org/pypi/' + libraryToInstall + '/json',
                                headers={"Accept": "application/json"})
        responseInfo = response.json().get("info")
        requires_pythonResult = responseInfo.get("requires_python")

        if requires_pythonResult is not None and requires_pythonResult != "":
            constraitsPythonVersions = requires_pythonResult.split(",")

            for thisPytonVersion in constraitsPythonVersions:
                if "!=" in thisPytonVersion:
                    elem = thisPytonVersion.split("!=")
                    # TODO Fazer coisas
                    notPythonSupported.append(elem[1])
                if ">=" in thisPytonVersion:
                    elem = thisPytonVersion.split(">=")
                    greaterOrEqualThan.append(elem[1])
                elif "<=" in thisPytonVersion:
                    elem = thisPytonVersion.split("<=")
                    lesserOrEqualThan.append(elem[1])
                elif "<" in thisPytonVersion:
                    elem = thisPytonVersion.split("<")
                    lesserThan.append(elem[1])
                elif ">" in thisPytonVersion:
                    elem = thisPytonVersion.split(">")
                    greaterThan.append(elem[1])

            print(requires_pythonResult)

    ### calculation of  the lower index
    greaterOrEqualThan = sorted(greaterOrEqualThan, reverse=True)
    greaterThan = sorted(greaterThan, reverse=True)
    greaterOrEqualElem = getValidPythonVersion(greaterOrEqualThan)

    if greaterOrEqualElem is None:
        # default python version
        greaterOrEqualElem = "3.7.0"

    greaterThanElem = getValidPythonVersion(greaterThan)
    if greaterThanElem is None:
        greaterThanElem = ""

    if greaterOrEqualElem <= greaterThanElem:
        indexPythonVersion = ALL_PYTHON_VERSIONS.index(greaterThanElem)
        lowerIndex = indexPythonVersion + 1
    else:
        lowerIndex = ALL_PYTHON_VERSIONS.index(greaterOrEqualElem)

    ### calculation of  the upper index
    lesserOrEqualThan = sorted(lesserOrEqualThan)
    lesserThan = sorted(lesserThan)

    lesserOrEqualThanElem = getValidPythonVersion(lesserOrEqualThan)
    if lesserOrEqualThanElem is None:
        # default python version
        lesserOrEqualThanElem = ALL_PYTHON_VERSIONS[len(ALL_PYTHON_VERSIONS) - 1]

    lesserThanElem = getValidPythonVersion(lesserThan)
    if lesserThanElem is None:
        lesserThanElem = ""

    if lesserOrEqualThanElem >= lesserThanElem != "":
        indexPythonVersion = ALL_PYTHON_VERSIONS.index(lesserThanElem)
        upperIndex = indexPythonVersion - 1
    else:
        upperIndex = ALL_PYTHON_VERSIONS.index(lesserOrEqualThanElem)

    if lowerIndex <= upperIndex:
        x = ALL_PYTHON_VERSIONS[lowerIndex]
        return x
    else:
        raise ValueError("Sorry, the python versions are not compatibles")


def getValidPythonVersion(greaterOrEqualThan):
    ALL_PYTHON_VERSIONS = settingsPython.getAllPythonVersions()
    while len(greaterOrEqualThan) > 0:
        greaterOrEqualElem = greaterOrEqualThan.pop(0)
        if greaterOrEqualElem not in ALL_PYTHON_VERSIONS:
            greaterOrEqualElem += ".0"
            if greaterOrEqualElem in ALL_PYTHON_VERSIONS:
                return greaterOrEqualElem
        else:
            return greaterOrEqualElem
    return None
