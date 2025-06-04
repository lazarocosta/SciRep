import os
import requests
from bs4 import BeautifulSoup
import shutil

from settings import copyFiles


def createJavaEnvironment_linux(myProjectFolder, javaVersionString, linuxVersion):
    # file.write("FROM " + dockerImage + "\n")
    # file.write("RUN chmod a+x ./run_java_script.sh\n")
    # file.write('CMD ./run_java_script.sh "' + jarFile + '"\n\n')

    # ['openjdk-17', 'openjdk-16','openjdk-13',"openjdk-11","openjdk-8"]
    # FROM ubuntu:22.04 =versao (entre 8 e 17) deu aqui deu aqui java
    # FROM ubuntu:20.04 versao (entre 8 e 17) deu aqui
    # FROM ubuntu:18.04 versao (entre 8 e 11) deu aqui


    ##[JDK:8, JDK:11, JDK:13, JDK:16, JDK:17]

    allowJavaVersion = [8, 11, 13, 16, 17]
    file = open(myProjectFolder + "/Dockerfile", "a")
    javaVersion = javaVersionString.split("JDK:")[1]

    if int(javaVersion) not in allowJavaVersion:
        file.close()
        raise ValueError("Java version is not available")

    if linuxVersion is None:
        if int(javaVersion) > 11:
            my_linuxVersion = "20.04"
            my_linuxVersion = "22.04"
        else:
            my_linuxVersion = "18.04"
            my_linuxVersion = "20.04"
            my_linuxVersion = "22.04"
        file.write("FROM ubuntu:" + my_linuxVersion + "\n")
        file.write("RUN apt update && apt upgrade -y\n")
    else:
        my_linuxVersion = linuxVersion

    if int(javaVersion) < 15:
        file.write("RUN apt install -y openjdk-" + javaVersion + "-jre\n")

    file.write("RUN apt install -y openjdk-" + javaVersion + "-jdk\n")
    file.write("RUN apt install -y maven\n\n")

    #Nao é necessario fazer isto
    #     file.write('COPY --from=' + javaDockerImage['dockerImage'] + ' ' + javaDockerImage[
    #         'JAVA_HOME'] + ' /usr/local/my-java\n')
    #     file.write('ENV JAVA_HOME /usr/local/my-java\n')
    #     file.write('RUN update-alternatives --install /usr/bin/java java /usr/local/my-java/bin/java 2000\n\n')
    #     file.write('COPY --from=' + javaDockerImage['dockerImage'] + ' /usr/share/maven /usr/share/maven\n')
    #     file.write('ENV M2_HOME /usr/share/maven\n')
    #     file.write('ENV M2 $M2_HOME/bin\n')
    #     file.write('RUN update-alternatives --install /usr/bin/mvn mvn /usr/share/maven/bin/mvn 2000\n\n')
    #     file.write('RUN mvn clean package\n')

    copyFiles(file, linuxVersion)

    #file.write("RUN mvn clean package\n")
    file.close()
    return my_linuxVersion


def createJavaEnvironment_windows(myProjectFolder, javaVersionString, windowsVersion):
    ##[JDK:14, JDK:15, JDK:16, JDK:17, JDK:19]

    allowJavaVersion = [14, 15, 16, 17, 19]
    file = open(myProjectFolder + "/Dockerfile", "a")
    javaVersion = javaVersionString.split("JDK:")[1]

    if int(javaVersion) not in allowJavaVersion:
        file.close()
        raise ValueError("Java version is not available")

    if windowsVersion is None:
        file.write("FROM mcr.microsoft.com/windows/servercore:ltsc2019\n")
        my_windowsVersion = True
    else:
        my_windowsVersion = windowsVersion

    # https://jdk.java.net/14/
    # https://download.java.net/openjdk/jdk14/ri/openjdk-14+36_windows-x64_bin.zip
    # https://download.java.net/openjdk/jdk15/ri/openjdk-15+36_windows-x64_bin.zip
    # https://download.java.net/openjdk/jdk16/ri/openjdk-16+36_windows-x64_bin.zip
    # https://download.java.net/openjdk/jdk17/ri/openjdk-17+35_windows-x64_bin.zip
    # https://download.java.net/openjdk/jdk18/ri/openjdk-18+36_windows-x64_bin.zip
    # https://download.java.net/openjdk/jdk19/ri/openjdk-19+36_windows-x64_bin.zip
    if int(javaVersion) == 17:
        file.write("ENV JAVA_VERSION 17\n")
        file.write("ENV PLUS_VALUE 35\n")
    else:
        file.write("ENV JAVA_VERSION" + javaVersion + "\n")
        file.write("ENV PLUS_VALUE 36\n")

    file.write("# Download and extract JDK\n")
    file.write(
        'ENV FILE_URL "https://download.java.net/openjdk/jdk${JAVA_VERSION}/ri/openjdk-${JAVA_VERSION}+${PLUS_VALUE}_windows-x64_bin.zip"\n')
    file.write("ADD ${FILE_URL} C:/jdk.zip\n")
    file.write("#unzip\n")
    file.write('''RUN powershell -Command "expand-archive -Path 'c:\jdk.zip' -DestinationPath 'c:\jdk'"\n''')
    file.write('''RUN powershell -Command "Remove-Item -Path 'c:\jdk.zip'"\n''')

    file.write("# Set Java home environment variable\n")
    file.write('RUN setx -m JAVA_HOME "C:\jdk\jdk-%JAVA_VERSION%"\n')
    file.write('RUN setx -m PATH "%PATH%;%JAVA_HOME%\\bin"\n')

    file.write("# Set environment variables for Maven\n")
    file.write("ENV MAVEN_VERSION 3.8.3\n")
    file.write('ENV MAVEN_HOME "C:\maven\\apache-maven-${MAVEN_VERSION}"\n')

    file.write("# Download and install Maven\n")

    file.write(
        "ADD https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/${MAVEN_VERSION}/apache-maven-${MAVEN_VERSION}-bin.zip C:/maven.zip\n")
    file.write('''RUN powershell -Command "expand-archive -Path 'c:\maven.zip' -DestinationPath 'c:\maven'"\n''')
    file.write('''RUN powershell -Command "Remove-Item -Path 'c:\maven.zip'"\n''')

    file.write("# Add Maven bin directory to the PATH\n")
    file.write('RUN setx /M PATH "%PATH%;%MAVEN_HOME%\\bin"\n')

    copyFiles(file, windowsVersion)

    file.write("RUN mvn clean package\n")
    file.close()
    return my_windowsVersion

#
# def createJavaEnvironment2(myProjectFolder, javaDockerImage, writeFile, linuxVersion):
#     if writeFile:
#         return writeDockerFileEnvironment(myProjectFolder, javaDockerImage, linuxVersion)
#     else:
#         return {'dockerImage': javaDockerImage,
#                 "JAVA_HOME": getJavaHome(javaDockerImage)
#                 }

#
# def writeDockerFileEnvironment(myProjectFolder, javaVersionString, linuxVersion):
#     # file.write("FROM " + dockerImage + "\n")
#     # file.write("RUN chmod a+x ./run_java_script.sh\n")
#     # file.write('CMD ./run_java_script.sh "' + jarFile + '"\n\n')
#
#     # ['openjdk-17', 'openjdk-16','openjdk-13',"openjdk-11","openjdk-8"]
#     # FROM ubuntu:22.04 =versao (entre 8 e 17) deu aqui deu aqui java
#     # FROM ubuntu:20.04 versao (entre 8 e 17) deu aqui
#     # FROM ubuntu:18.04 versao (entre 8 e 11) deu aqui
#
#     allowJavaVersion = [8, 11, 13, 16, 17]
#     file = open(myProjectFolder + "/Dockerfile", "a")
#     if linuxVersion is None:
#         if int(javaVersionString) > 11:
#             my_linuxVersion = "20.04"
#             my_linuxVersion = "22.04"
#         else:
#             my_linuxVersion = "18.04"
#             my_linuxVersion = "20.04"
#             my_linuxVersion = "22.04"
#         file.write("FROM ubuntu:" + my_linuxVersion + "\n")
#         file.write("RUN apt update\n")
#         file.write("RUN apt upgrade -y\n")
#     else:
#         my_linuxVersion = linuxVersion
#
#     javaVersion = javaVersionString.split("openjdk-")[1]
#     if javaVersion in allowJavaVersion:
#         if javaVersion < 15:
#             file.write("RUN apt install -y openjdk-" + javaVersion + "-jre\n")
#
#         file.write("RUN apt install -y openjdk-" + javaVersion + "-jdk\n")
#         file.write("RUN apt install -y maven\n\n")
#
#         if linuxVersion is None:
#             file.write("WORKDIR /files\n")
#             file.write("COPY ./files .\n\n")
#
#         file.write("RUN mvn clean package\n")
#         file.close()
#         return my_linuxVersion
#     else:
#         file.close()
#         raise ValueError("Java version is not available")


# JAVA
# RUN  apt update &&  apt upgrade -y

# RUN apt install -y openjdk-8-jre
# RUN apt install -y openjdk-8-jdk

# RUN apt install -y openjdk-11-jdk
# RUN apt install -y openjdk-11-jre

# RUN apt install -y openjdk-13-jdk
# RUN apt install -y openjdk-13-jre

# RUN apt install -y openjdk-14-jdk não existe

# RUN apt install -y openjdk-16-jdk

# RUN apt install -y openjdk-17-jdk
# RUN apt install -y maven

#
# def getJavaHome(mavenDockerImage):
#     version = mavenDockerImage.split("maven:")[1]
#     r = requests.get(url="https://hub.docker.com/v2/repositories/library/maven/tags/" + version + "/images")
#
#     data = r.json()
#     for architecture in data:
#         if architecture["architecture"] == "amd64":
#             layers = architecture["layers"]
#             for layer in layers:
#                 instruction = layer["instruction"]
#                 if "JAVA_HOME" in instruction:
#                     instructionsSplited = instruction.split(" ")
#                     for myIntruction in instructionsSplited:
#                         if "JAVA_HOME" in myIntruction:
#                             javaHome = myIntruction.split("JAVA_HOME=")[1]
#                             return javaHome
#         break
#     # TODO check this situation
#     return None

#
# def getdockerImageToInstall(source):
#     result = {
#         'dockerImage': '',
#         'JAVA_HOME': ''
#     }
#
#     if source == '1.8':
#         result['dockerImage'] = 'maven:3.8.6-jdk-8-slim'  # 20
#     # elif source == '1.7':
#     #     result['dockerImage'] = 'maven:3.6.1-jdk-7-slim'
#     # elif source == '1.9':
#     #     result['dockerImage'] = 'maven:3.5-jdk-9-slim'  # 37
#     # elif source == '10':
#     #     result['dockerImage'] = 'maven:3.6-jdk-10-slim'  # 23
#     elif source == '11':
#         result['dockerImage'] = 'maven:3.8.6-jdk-11-slim'  #
#     # elif source == '12':
#     #     result['dockerImage'] = 'maven:3.6.0-jdk-12-alpine'  #
#     # elif source == '13':
#     #     result['dockerImage'] = 'maven:3.6.1-jdk-13-alpine'  #
#     elif source == '14':
#         result['dockerImage'] = 'maven:3.6.3-openjdk-14-slim'  #
#     elif source == '15':
#         result['dockerImage'] = 'maven:3.8-openjdk-15-slim'  #
#     elif source == '16':
#         result['dockerImage'] = 'maven:3.8-openjdk-16-slim'  #
#     elif source == '17':
#         result['dockerImage'] = 'maven:3.8.5-openjdk-17-slim'  #
#     elif source == '18':
#         result['dockerImage'] = 'maven:3.8.6-openjdk-18-slim'  #
#     elif source == '19':
#         result['dockerImage'] = 'maven:3.8-eclipse-temurin-19-alpine'  #
#     else:
#         result['dockerImage'] = 'maven:3.8.6-jdk-8-slim'  #
#
#     result['JAVA_HOME'] = getJavaHome(result['dockerImage'])
#     return result

#
# def createJavaEnvironmentComplex(myProjectFolder, projectFiles, writeFile):
#     # if not hasRequirementsFile:
#     # tree = ET.parse(projectFiles + "/pom.xml")
#     # root = tree.getroot()
#     # print(ET.tostring(root, 'utf-8'))
#     # artifactId=None
#     # groupId=None
#     # for child in root:
#     #     mychild= child.tag.split("}")
#     #     if len(mychild) > 1:
#     #         if mychild[1] == "artifactId":
#     #             artifactId = child.text
#     #         elif mychild[1] == "groupId":
#     #             groupId = child.text
#     #
#     shutil.copy(os.getcwd() + './configProgrammingLanguages/run_java_script.sh', projectFiles + "/run_java_script.sh")
#     with open(projectFiles + "/pom.xml") as r:
#         text = r.read()
#         soup = BeautifulSoup(text, "xml")
#
#         source = 1.8  # default
#         jarFile = "NULL"
#         plugins = soup.find_all("plugin")
#
#         for plugin in plugins:
#             plugin_encoded = bytes(str(plugin), 'UTF-8')
#             myPlugin = BeautifulSoup(plugin_encoded, "xml")
#             artifactIdOfMyPlugin = myPlugin.find("artifactId")
#
#             if artifactIdOfMyPlugin is not None:
#                 if artifactIdOfMyPlugin.text == "maven-compiler-plugin":
#                     # mavenVersion = myPlugin.find("version").text
#                     configuration = myPlugin.find("configuration")
#                     configuration_encoded = bytes(str(configuration), 'UTF-8')
#                     myConfiguration = BeautifulSoup(configuration_encoded, "xml")
#                     source = myConfiguration.find("source")
#                     if source is not None:
#                         source = source.text
#                     release = myConfiguration.find("release")
#
#                     if release is not None:
#                         release = release.text
#
#                 if artifactIdOfMyPlugin.text == "maven-assembly-plugin":
#                     configuration = myPlugin.find("configuration")
#                     configuration_encoded = bytes(str(configuration), 'UTF-8')
#                     myConfiguration = BeautifulSoup(configuration_encoded, "xml")
#                     descriptorRefs = myConfiguration.find("descriptorRefs")
#                     descriptorRefs_encoded = bytes(str(descriptorRefs), 'UTF-8')
#                     mydescriptorRefs = BeautifulSoup(descriptorRefs_encoded, "xml")
#                     jarFile = mydescriptorRefs.find("descriptorRef")
#
#                     if jarFile is not None:
#                         jarFile = jarFile.text
#
#         mavenTarget = soup.find("maven.compiler.target")
#         if mavenTarget is not None:
#             source = mavenTarget.text
#         elif release is not None:
#             source = release
#     dockerImage = getdockerImageToInstall(source)

#     if writeFile:
#         writeDockerFileEnvironment(myProjectFolder, dockerImage['dockerImage'])
#         return
#     else:
#         return dockerImage
