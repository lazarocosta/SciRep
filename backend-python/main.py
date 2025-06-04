# import json
import shutil
from copy import copy

import logging
import os
import tarfile
import uuid
from time import sleep
from zipfile import ZipFile
from random import randrange
from datetime import datetime

from docker import errors
from flask import Flask, request, send_from_directory, Response
from flask_cors import CORS, cross_origin

import settingsPython
from configProgrammingLanguages.cPlusPlusEnvironment import createCPlusPlusEnvironment_linux, \
    createCPlusPlusEnvironment_windows
from configProgrammingLanguages.javaEnvironment import createJavaEnvironment_linux, createJavaEnvironment_windows
from configProgrammingLanguages.jupyterEnvironment import createJupyterNotebookEnvironment
from configProgrammingLanguages.perlEnvironment import perlEnvironment_linux, perlEnvironment_windows
from configProgrammingLanguages.pythonEnvironment import validatePythonEnvironment, createPythonEnvironment_linux, \
    createPythonEnvironment_windows
from configProgrammingLanguages.rEnviroment import rEnvironment_linux, rEnvironment_windows
from configProgrammingLanguages.shellEnvironment import createShellEnvironment
from controllers.database import buildDockerImageDatabase, runDockerContainerDatabase
from controllers.project import getProjectLocation, find_files, read_first_50_lines
from model.model import hasSession, getSessions, deleteSessionsFromDatabase, addConfigurationToDatabase, \
    getConfiguration, addDatabaseConfigurationToDatabase, addExecutioToDatabase
from packageExperiment.database import writeFileDatabase
from packageExperiment.linux import writeLinuxFile
from packageExperiment.windows import writeWindowsFIle
from settings import *

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def buildDockerFile(requestData, projectUuid, projectFiles, myProjectFolder):
    if "useMyDockerfile" not in requestData:
        useMyDockerFile = False
    else:
        try:
            useMyDockerFile = json.loads(requestData["useMyDockerfile"])
        except Exception as e:
            print(str(e))
            return makeResponse({'message': "useMyDockerFile parameter must be a string 'true' or 'false'"}, 404, True)

    hasRequirementsFile = None
    if not useMyDockerFile:
        if "planguages" not in requestData:
            return makeResponse({"message": "The programming languages to execute is missing"}, 404, True)
        if type(requestData["planguages"]) != list:
            return makeResponse({"message": "The Programming languages variable needs be a list"}, 404, True)

        pythonDependenciesToAddManually = []
        if "dependenciesToAdd" in requestData:
            dependenciesToAdd = requestData["dependenciesToAdd"]
            # languages = list(dependenciesToAdd.keys())
            # for language in languages:
            #     if language == "python":
            #         pythonDependenciesToAddManually = dependenciesToAdd.get("python")
            pythonDependenciesToAddManually = dependenciesToAdd
        if "manualConfigs" in requestData:
            commandsToAdd = requestData["manualConfigs"]
        else:
            commandsToAdd = []

        if "operatingSystem" in requestData:
            operatingSystem = requestData["operatingSystem"]
            if operatingSystem not in ["Unix Shell", "Windows"]:
                return makeResponse({"message": "Operating system must be Unix Shell or Windows"}, 404, True)
        else:
            operatingSystem = "Unix Shell"

        # todo retirar
        # delete content from the Dockerfile
        open(myProjectFolder + "/Dockerfile", "w").close()
        try:
            planguagesArray = requestData["planguages"]
            mydict = {}
            for obj in requestData["planguages"]:
                if obj['notUsed'] is not True:
                    mydict[obj['pl']] = obj

            if operatingSystem == "Unix Shell":
                linuxVersion = None

                if "r" in mydict:
                    rversionString = mydict['r']['versionSelected']
                    # rversionString = "4"
                    linuxVersion = rEnvironment_linux(myProjectFolder, rversionString, linuxVersion=linuxVersion)

                if "perl" in mydict:
                    perlversionString = mydict['perl']['versionSelected']
                    # rversionString = "4"
                    linuxVersion = perlEnvironment_linux(myProjectFolder, perlversionString, linuxVersion=linuxVersion)

                if "cPlusPlus" in mydict:
                    gccVersionString = mydict['cPlusPlus']['versionSelected']
                    linuxVersion = createCPlusPlusEnvironment_linux(myProjectFolder, gccVersionString,
                                                                    linuxVersion=linuxVersion)

                if "java" in mydict:
                    # requirementsFile = getFileNamedAs(projectUuid, "pom.xml")
                    # hasRequirementsFile = True if len(requirementsFile) > 0 else False
                    javaVersion = mydict['java']['versionSelected']
                    linuxVersion = createJavaEnvironment_linux(myProjectFolder, javaVersion, linuxVersion=linuxVersion)

                if "python" in mydict:
                    # requirementsFile = getFileNamedAs(projectUuid, "requirements.txt")
                    # hasRequirementsFile = True if len(requirementsFile) > 0 else False
                    if "hasRequirementsFile" in requestData:
                        hasRequirementsFile = json.loads(requestData["hasRequirementsFile"])
                    else:
                        hasRequirementsFile = False
                    pythonVersion = mydict['python']['versionSelected']
                    createPythonEnvironment_linux(myProjectFolder, hasRequirementsFile, pythonDependenciesToAddManually,
                                                  pythonVersion, linuxVersion=linuxVersion)

                if "jupyterNotebook" in mydict:
                    createJupyterNotebookEnvironment(myProjectFolder, projectFiles)

                if "shell" in mydict:
                    # shellVersion = mydict['shell']['versionSelected']
                    linuxVersion = createShellEnvironment(myProjectFolder, linuxVersion=linuxVersion)

            if operatingSystem == "Windows":
                windowsVersion = None

                # languagesVersion= json.loads(requestData["versionSelected"])
                # languagesVersion = requestData["versionSelected"]
                if "r" in mydict:
                    rversionString = mydict['r']['versionSelected']
                    # rversionString = "4"
                    windowsVersion = rEnvironment_windows(myProjectFolder, rversionString,
                                                          windowsVersion=windowsVersion)

                if "perl" in mydict:
                    perlversionString = mydict['perl']['versionSelected']
                    windowsVersion = perlEnvironment_windows(myProjectFolder, perlversionString,
                                                             windowsVersion=windowsVersion)

                if "cPlusPlus" in mydict:
                    gccVersionString = mydict['cplusplus']['versionSelected']
                    windowsVersion = createCPlusPlusEnvironment_windows(myProjectFolder, gccVersionString,
                                                                        windowsVersion=windowsVersion)

                if "java" in mydict:
                    # requirementsFile = getFileNamedAs(projectUuid, "pom.xml")
                    # hasRequirementsFile = True if len(requirementsFile) > 0 else False
                    javaVersion = mydict['java']['versionSelected']
                    windowsVersion = createJavaEnvironment_windows(myProjectFolder, javaVersion,
                                                                   windowsVersion=windowsVersion)

                if "python" in mydict:
                    # requirementsFile = getFileNamedAs(projectUuid, "requirements.txt")
                    # hasRequirementsFile = True if len(requirementsFile) > 0 else False
                    if "hasRequirementsFile" in requestData:
                        hasRequirementsFile = json.loads(requestData["hasRequirementsFile"])
                    else:
                        hasRequirementsFile = False
                    pythonVersion = mydict['python']['versionSelected']
                    createPythonEnvironment_windows(myProjectFolder, hasRequirementsFile,
                                                    pythonDependenciesToAddManually,
                                                    pythonVersion, windowsVersion=windowsVersion)
        except Exception as e:
            print(str(e))
            raise Exception(str(e))

        # TODO     Alterar cd por workdir
        if len(commandsToAdd) > 0:

            file = open(myProjectFolder + "/Dockerfile", "a", )
            for commandToAdd in commandsToAdd:
                file.write("RUN " + commandToAdd + "\n")
            file.close()
        path = myProjectFolder
    else:
        path = projectFiles
    return {"path": path, "hasRequirementsFile": hasRequirementsFile}


@app.route("/<projectUuid>/build-docker-image", methods=['POST'])
@cross_origin()
def buildDockerImage(projectUuid):
    requestData = request.get_json()

    configurationForm = requestData['configurationForm']
    dockerfile, dockerfileDatabase = configurationForm['dockerfile'], configurationForm['dockerfileDatabase']

    projectLocation = getProjectLocation(projectUuid)
    projectFiles, myProjectFolder = projectLocation["projectFiles"], projectLocation["myProjectFolder"]

    try:
        dockerClientResult = startDockerClient()
        dockerClient, port = dockerClientResult["dockerClient"], dockerClientResult["port"]

        path = myProjectFolder
        number = datetime.now().strftime("%Y%m%d%H%M%S")

        updateDockerFileIfNecessary(dockerfile, "Dockerfile", path)
        dockerImageBuilt = dockerClient.images.build(path=path, tag=projectUuid + ":" + number, rm=True)

        # if len(dockerImageBuilt[0].tags) == 1:
        networkName = projectUuid
        createNetworkIfNotExists(dockerClient, networkName)

        # projectImage = dockerClient.images.get(dockerImageBuilt[0].tags[0])
        dockerImageBuiltFiltered = [s for s in dockerImageBuilt[0].tags if projectUuid in s]
        dockerTagsLenght = len(dockerImageBuiltFiltered) - 1

        configurationName, operatingSystem, = configurationForm['configureName'].strip(), configurationForm[
            'operatingSystem']

        if configurationName == "" or operatingSystem == "":
            raise Exception("the values of configureName and  operatingSystem are required")

        configure = {'configurationName': configurationName, 'operatingSystem': operatingSystem,
                     'dockerImageID': dockerImageBuiltFiltered[dockerTagsLenght]}
        if configurationForm['port'] != "":
            port = {'port': configurationForm['port']}
            configure = {**configure, **port}
        configurationNode = addConfigurationToDatabase(projectUuid, configure)
        # else:
        #   dockerImageBuilt = deleteRepetedDockerImages(dockerClient, dockerImageBuilt, projectUuid)

        dockerImageBuiltDatabase = None
        if "DBhas" in configurationForm and "dbConfiguration" in configurationForm:
            if configurationForm["DBhas"] is True:
                updateDockerFileIfNecessary(dockerfileDatabase, "DockerfileDatabase", path)
                dbdockerImageName = projectUuid + "-" + configurationForm['DBName'].lower() + ":" + str(number)

                dockerImageBuiltDatabase = dockerClient.images.build(path=path, dockerfile="DockerfileDatabase",
                                                                     tag=dbdockerImageName,
                                                                     rm=True)

                # todo==1
                # if len(dockerImageBuiltDatabase[0].tags) == 1:

                # databaseImage = dockerClient.images.get(dockerImageBuiltDatabase[0].tags[0])
                # databasaseDockerImageID = str(number)dockerImageBuiltDatabase[0].tags[databaseTagsLenght].split(":")[1]

                # Use a list comprehension to filter the strings
                search_term = projectUuid + "-" + configurationForm['DBName'].lower()
                dockerImageBuiltDatabaseFiltered = [s for s in dockerImageBuiltDatabase[0].tags if search_term in s]
                databaseTagsLenght = len(dockerImageBuiltDatabaseFiltered) - 1
                # databasaseDockerImageID = str(number)

                databaseConfigurationName = configurationForm['dbConfiguration']['DBconfigureName'].strip()
                databaseConfigurationPort = configurationForm['dbConfiguration']['DBport']
                dbnameConnection = configurationForm['dbConfiguration']['DBnameConnection']
                dbName = configurationForm['DBName']

                if databaseConfigurationName == "":
                    raise Exception("the value of databaseConfigurationName is required")
                configure = {'configurationName': configurationName, 'dbName': dbName,
                             'dbPort': databaseConfigurationPort, 'dbnameConnection': dbnameConnection,
                             'dbdockerImageName': dbdockerImageName}
                containerList = addDatabaseConfigurationToDatabase(configurationNode.id, configure)
                # else:
                # todo esta mal para apagar as imagens das base de dados
                #   dockerImageBuiltDatabase = deleteRepetedDockerImages(dockerClient, dockerImageBuiltDatabase,
                #                                                     projectUuid)

        if not dockerImageBuiltDatabase:
            return makeResponse({"dockerImageID": dockerImageBuiltFiltered[dockerTagsLenght]}, 201, True)
        else:
            return makeResponse({"dockerImageID": dockerImageBuiltFiltered[dockerTagsLenght],
                                 "dockerImageIDDatabase": dockerImageBuiltDatabaseFiltered[databaseTagsLenght]},
                                201, True)
    except Exception as e:
        print(str(e))
        return makeResponse({'message': str(e)}, 404, True)


def deleteRepetedDockerImages(dockerClient, dockerImageBuilt, projectUuid):
    dockerImagestoRemove = [elemento.split(":")[1] for elemento in dockerImageBuilt[0].tags]
    databasedockerImagestoRemove = sorted(map(int, dockerImagestoRemove))
    while len(dockerImagestoRemove) > 1:
        firstElement = dockerImagestoRemove.pop()
        try:
            dockerClient.images.remove(projectUuid + ":" + str(firstElement))
        except Exception as e:
            print(str(e))
    dockerImageBuilt[0].tags[0] = projectUuid + ":" + str(dockerImagestoRemove[0])
    return dockerImageBuilt


def updateDockerFileIfNecessary(dockerfile, dockerfileName, path):
    try:
        with open(path + '/' + dockerfileName, 'r') as file:
            file_content = file.read()

            if file_content != dockerfile:
                raise Exception("write content")
    except Exception as e:
        with open(path + "/" + dockerfileName, 'w') as file:
            file.write(dockerfile)
        print(f"String saved to {path}/{dockerfileName} successfully.")


@app.route("/<projectUuid>/build-docker-file", methods=['POST'])
@cross_origin()
def buildDockerFileMain(projectUuid):
    requestData = json.loads(request.data)

    projectLocation = getProjectLocation(projectUuid)
    projectFiles, myProjectFolder = projectLocation["projectFiles"], projectLocation["myProjectFolder"]

    try:
        dockerClientResult = startDockerClient()
        dockerClient, port = dockerClientResult["dockerClient"], dockerClientResult["port"]
        path = myProjectFolder

        buildDockerFile(requestData, projectUuid, projectFiles, myProjectFolder)

        if requestData['DBhas'] == True and "dbConfiguration" in requestData:
            print("has_database")
            #     if requestData["database"] is not None and requestData["databaseParameters"] is not None:
            dockerfile_template = buildDockerImageDatabase(myProjectFolder, requestData["DBName"],
                                                           requestData["dbConfiguration"])
            with open(path + "/Dockerfile") as f:
                contents = f.read()
                print(contents)
            return makeResponse({"dockerfile": contents, "dockerfileDatabase": dockerfile_template}, 201, True)
        #
        #     if not dockerImageBuiltDatabase:
        #         return makeResponse({"dockerImageID": dockerImageBuilt[0].tags[0], "dependencies": contents}, 201, True)
        #     else:
        #         return makeResponse({"dockerImageID": dockerImageBuilt[0].tags[0],
        #                              "dockerImageIDDatabase": dockerImageBuiltDatabase, "dependencies": contents}, 201,
        #                             True)
        # else:
        #     if not dockerImageBuiltDatabase:
        #         with open(path+ "/Dockerfile") as f:
        #             contents = f.read()
        #             print(contents)
        #         return makeResponse({"dockerfile": contents}, 201, True)
        #     else:
        #         return makeResponse({"dockerImageID": dockerImageBuilt[0].tags[0],
        #                              "dockerImageIDDatabase": dockerImageBuiltDatabase}, 201, True)
        else:
            with open(path + "/Dockerfile") as f:
                contents = f.read()
                print(contents)
            return makeResponse({"dockerfile": contents}, 201, True)

    except Exception as e:
        print(str(e))
        return makeResponse({'message': str(e)}, 404, True)


@app.route("/<projectUuid>/get-configuration", methods=['GET'])
@cross_origin()
def getDockerImages(projectUuid):
    try:
        configuration = getConfiguration(projectUuid)
        return makeResponse({"configuration": configuration}, 201, True)
    except Exception as e:
        print(str(e))
        return makeResponse({'message': str(e)}, 404, True)


@app.route("/<projectUuid>/validates-docker-image", methods=['POST'])
@cross_origin()
def validatesDockerImage(projectUuid):
    requestData = json.loads(request.data)
    projectLocation = getProjectLocation(projectUuid)
    projectFiles, myProjectFolder = projectLocation["projectFiles"], projectLocation["myProjectFolder"]

    if "pythondependencies" not in requestData:
        return makeResponse({"message": "python dependencies is missing"}, 404, True)
    else:
        pythondendencies = requestData["pythondependencies"]

    #    pythondendencies = ["beautifulsoup4==4.12.2", "Requests==2.28.2"]

    if "tagId" not in requestData:
        return makeResponse({"message": "tagId is missing"}, 404, True)
    else:
        tagId = requestData["tagId"]

    try:
        dockerClientResult = startDockerClient()
        dockerClient, port = dockerClientResult["dockerClient"], dockerClientResult["port"]

        validatePythonEnvironment(myProjectFolder, projectFiles, pythondendencies)

        """    # Get the previously built image"""
        base_imageList = dockerClient.images.get(projectUuid + ":" + tagId)

        # myDockerImage= None
        # for dockerImage in base_imageList.tags:
        #     if dockerImage == projectUuid+ ":"+tagId:
        #         myDockerImage= dockerImage
        #         break
        #
        # if myDockerImage is None:
        #     return makeResponse({'message': "Docker tage name is not exists"}, 404, True)

        # Create a new Docker image from the base image
        new_image, logs = dockerClient.images.build(
            path=myProjectFolder,  # Use the current directory as the build context
            tag=projectUuid + ":" + str(int(tagId) + 1),
            dockerfile="Newdockerfile",  # Use the default Dockerfile name
            cache_from=[base_imageList.id]  # Use the previously built image as the cache
        )
        return makeResponse({"dockerImageID": new_image.tags[0]}, 201, True)
    except Exception as e:
        print(str(e))
        return makeResponse({'message': str(e)}, 404, True)


@app.route("/<projectUuid>/run-container", methods=['POST'])
@cross_origin()
def runDockerContainer(projectUuid):
    requestData = request.get_json()['configurationForm']
    configurationToUse = request.get_json()['configurationToUse']

    """    # Get the previously built image
    base_image = client.images.get(base_image)

    # Create a new Docker image from the base image
    new_image, logs = client.images.build(
        path='.',  # Use the current directory as the build context
        tag=new_image_name,
        dockerfile='Dockerfile',  # Use the default Dockerfile name
        cache_from=base_image.id  # Use the previously built image as the cache
    )"""

    """  # Get the container
        container = client.containers.get(container_name)

        # Copy the file from the container to a temporary file
        tmp_file, stat = container.get_archive(container_path)
        with open(local_path, 'wb') as f:
            for chunk in tmp_file:
                f.write(chunk)
    """
    if "command" in requestData:
        command = requestData["command"].split()

    else:
        return makeResponse({"message": "The command is required"}, 404, True)

    if "tagId" in requestData:
        tagId = requestData["tagId"]
    else:
        return makeResponse({"message": "The tagId is required"}, 404, True)

    # if "key" not in requestData or "fullPath" not in requestData:
    #   return makeResponse({"message": "The File to execute is missing"}, 404, True)

    # key, fullPath, tagId, commandToExecute = requestData["key"], requestData["fullPath"], requestData["tagId"], \
    #   requestData["command"]

    # projectLocation = getProjectLocation(projectUuid)
    # projectFiles, myProjectFolder = projectLocation["projectFiles"], projectLocation["myProjectFolder"]

    try:
        dockerClientResult = startDockerClient()

        dockerClient, port = dockerClientResult["dockerClient"], dockerClientResult["port"]

        networkName = projectUuid
        containerDatabase = None
        projectImage = dockerClient.images.get(configurationToUse['dockerImageID'])
        # projectImage = dockerClient.images.get("lazaro2" + ":" + "latest")

        if "port" in configurationToUse:
            port = configurationToUse["port"]
        else:
            port = None

        now = datetime.now()  # current date and time
        number = now.strftime("%Y%m%d%H%M%S")

        if configurationToUse['database'] is not None:
            if "dbnameConnection" in configurationToUse["database"]:
                databaseNameConnection = configurationToUse["database"]['dbnameConnection']
            else:
                databaseNameConnection = None
            dockerIdDatabase, databaseName = configurationToUse["database"]['dbdockerImageName'], \
                configurationToUse["database"]['dbName']

            containerDatabase = runDockerContainerDatabase(dockerIdDatabase, networkName, databaseName,
                                                           databaseNameConnection)

            if port is not None:
                container = dockerClient.containers.run(image=projectImage, name=projectUuid + "_" + number,
                                                        network=networkName, ports={port: port},
                                                        command=command,
                                                        volumes=['./' + tagId.replace(":", "_") + ':/files'],
                                                        detach=True)
            else:
                container = dockerClient.containers.run(image=projectImage, name=projectUuid + "_" + number,
                                                        network=networkName,
                                                        command=command,
                                                        volumes=['./' + tagId.replace(":", "_") + ':/files'],
                                                        detach=True)
        else:
            x = 1
            if port is not None:
                container = dockerClient.containers.run(image=projectImage, name=projectUuid + "_" + number,
                                                        network=networkName, ports={port: port},
                                                        command=command,
                                                        volumes=['./' + tagId.replace(":", "_") + ':/files'],
                                                        detach=True)
            else:
                # new_directory = '/ola'
                # command =  f'/bin/sh -c "cd {new_directory}"'
                # command= f'sh -c "cd {new_directory} && exec bash"'

                # command = ["echo", "Hello, Docker!"]
                # command = ["/bin/sh", "-c", 'echo 1 && echo 2']
                container = dockerClient.containers.run(image=projectImage, name=projectUuid + "_" + number,
                                                        command=command,
                                                        volumes=['./' + tagId.replace(":", "_") + ':/files'],
                                                        detach=True)
        if requestData['executionName']:
            print('ola')
            dataToAdd = {'executionName': requestData['executionName'],
                         'command': requestData['command']}

            addExecutioToDatabase(projectUuid, configurationToUse['configurationName'], dataToAdd)

        # addSessionToDatabase(projectUuid, container.id)

        # TODO para este caso nao asseguro a reproducibilidade
        if port is not None:
            return makeResponse(
                {"logs": "http://127.0.0.1:" + str(port), "message": "container is running, check this link"}, 201,
                True)

        waitToConclude(container)
        print(container.ports)
        containerLogs = container.logs()

        print(containerLogs)
        print(container.id)
        print(container.status)

        changes = container.diff()

        # for change in changes:
        #   print(change['Kind'], change['Path'])

        created_files = set()

        # for mount in container.attrs['Mounts']:
        #     if mount['Type'] == 'volume':
        #         volume_name = mount['Name']
        #         volume = dockerClient.volumes.get(volume_name)
        #         for file_info in volume.attrs['Mountpoint'].iterdir():
        #             if file_info.is_file():
        #                 created_files.add(str(file_info))

        for file in created_files:
            print(file)

        # if containerDatabase:
        #    containerDatabase.stop()

        # container.remove()
        return makeResponse({"logs": containerLogs.decode("utf-8")}, 201, True)
    except Exception as e:
        print(str(e))
        return makeResponse({'message': str(e)}, 404, True)


# def saveDockerImage(myProjectFolder, dockerImageName, dockerTagId):
#     try:
#         client = docker.from_env()
#     except Exception as e:
#         print(str(e))
#     raise Exception("Docker is not running")
#
#     try:
#         image = client.images.get(dockerImageName + ":" + dockerTagId)
#     except Exception as e:
#         print(str(e))
#     raise Exception("The docker image is not exists")
#
#
#     # f = open(myProjectFolder + '/' + dockerImageName + '.tar.gz', 'wb')
#     f = open(myProjectFolder + '/' + dockerImageName + '.tar', 'wb')
#
#     for chunk in image.save(named=True):
#         f.write(chunk)
#     f.close()
#


def saveDockerImage(myProjectFolder, dockerImageName, dockerTagId):
    try:
        client = docker.from_env()
        image = client.images.get(dockerImageName + ":" + dockerTagId)
    except Exception as e:
        print(str(e))
        raise Exception("Docker is not running")

    # f = open(myProjectFolder + '/' + dockerImageName + '.tar.gz', 'wb')
    f = open(myProjectFolder + '/' + dockerImageName + '.tar', 'wb')

    for chunk in image.save(named=True):
        f.write(chunk)
    f.close()


@app.route("/<projectUuid>/package", methods=['GET'])
@cross_origin()
def researchArtifact(projectUuid):
    requestData = json.loads(request.data)

    if "commands" in requestData:
        commands = requestData["commands"]
    else:
        return makeResponse({"message": "The command is required"}, 404, True)

    if "tagId" in requestData:
        dockerTagId = requestData["tagId"]
    else:
        return makeResponse({"message": "The tagId is required"}, 404, True)

    if "port" in requestData:
        port = requestData["port"]
    else:
        port = None

    if "dockerIdDatabase" in requestData and "database" in requestData:
        if "databaseNameConnection" in requestData:
            databaseNameConnection = requestData["databaseNameConnection"]
        else:
            databaseNameConnection = None
        dockerIdDatabase, databaseName = requestData["dockerIdDatabase"], requestData["database"]
    else:
        dockerIdDatabase = None
        databaseName = None
        databaseNameConnection = None

    projectLocation = getProjectLocation(projectUuid)
    projectFiles, myProjectFolder = projectLocation["projectFiles"], projectLocation["myProjectFolder"]

    # dockerFilepath = buildDockerFile(requestData, projectUuid, projectFiles, myProjectFolder)

    # calling function to get all file paths in the directory
    # file_paths = get_all_file_paths(projectFiles)

    # printing the list of all files to be zipped
    print('Following files will be zipped:')

    # writing files to a zipfile
    with ZipFile(myProjectFolder + '/' + projectUuid + '.zip', 'w') as zip:
        hasDatabase = False

        if dockerIdDatabase and databaseName:
            windowsFile = "runDatabase.bat"
            writeFileDatabase(myProjectFolder + "/" + windowsFile, "windows", databaseName, dockerIdDatabase,
                              databaseNameConnection, projectUuid)
            zip.write(myProjectFolder + "/" + windowsFile, "./" + windowsFile)

            linuxFile = "runDatabase.sh"
            writeFileDatabase(myProjectFolder + "/" + linuxFile, "linux", databaseName, dockerIdDatabase,
                              databaseNameConnection, projectUuid)
            zip.write(myProjectFolder + "/" + linuxFile, "./" + linuxFile)

            # saveDockerImage(myProjectFolder, databaseName, dockerIdDatabase)
            # zip.write(myProjectFolder + "/" + databaseName + ".tar.gz", "./" + databaseName + ".tar.gz")

            hasDatabase = True

        arrayFiles = writeWindowsFIle(myProjectFolder + "/", projectUuid, commands, dockerTagId, hasDatabase, port)
        arrayFiles += writeLinuxFile(myProjectFolder + "/", projectUuid, commands, dockerTagId, hasDatabase, port)

        for file in arrayFiles:
            zip.write(myProjectFolder + "/" + file, "./" + file)

        # saveDockerImage(myProjectFolder, projectUuid, dockerTagId)
        # zip.write(myProjectFolder + "/" + projectUuid + ".tar.gz", "./" + projectUuid + ".tar.gz")

        # zip.write(dockerFilepath + "/Dockerfile", "./Dockerfile")

        # Iterate over all the files in directory
        # for folderName, subfolders, filenames in os.walk(projectFiles):
        #     for filename in filenames:
        #         # create complete filepath of file in directory
        #         filePath = os.path.join(folderName, filename)
        #
        #         myfilePath = filePath.split(projectFiles + "\\")[1]
        #         # zip.write(filePath, basename(filePath))
        #         zip.write(filePath, "./files/" + str(myfilePath))
        zip.close()
    print('All files zipped successfully!')

    return send_from_directory(myProjectFolder, projectUuid + ".zip", as_attachment=True, mimetype="application/zip")

def snapshot_directory(path):
    files_snapshot = {}
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            stat = os.stat(filepath)
            files_snapshot[filepath] = {
                'size': stat.st_size,
                'mtime': stat.st_mtime
            }
    return files_snapshot


def process_container_diff(diff_list):
    added_files = []
    removed_files = []
    modified_files = []  # You may need additional logic to detect modifications

    for change in diff_list:
        path = change['Path']
        kind = change['Kind']

        if kind == 1:
            if path.startswith("/files"):
                added_files.append(path)
        elif kind == 2:
            removed_files.append(path)
        # For modifications, you may need to use additional logic or tools

    return added_files, removed_files, modified_files

if __name__ == '__main__':

    settingsPython.initializeAllPythonVersions()
    # TODO é necssario escrever FLASK_RUN_PORT=8080 nas variaveis de ambiente da execução para a porta a executar ser a correta
    app.run(host='127.0.0.1', port=8080)

    # TODO Correr experiencias com interface grafica
    # Não é necesario ter export no dockerfile, o container tem que ser corrido desta maneira
    # dockerClient.containers.run(image="web:2",  ports={4200:4200}, command="npm run start", name = "ola" + "_" + "4200", detach = True)
    #
