import config


def writeFileDatabase(FileDatabaseLocation, system, databaseName, dockerImageId, databaseNameConnection, projectUuid):
    file = open(FileDatabaseLocation, "w",newline='')

    if system == "Unix Shell":
        file.write("#!/bin/bash\n")
        file.write("echo 'Script is running...'\n")

    if system == "windows":
        file.write("@ECHO OFF\n")
        file.write("@ECHO Script is running...\n")

    # file.write("docker load --input " + databaseName + ".tar\n")
    file.write("docker load < " + databaseName + ".tar.gz\n")

    if databaseName == "mongo":
        ports = config.mongo['ports']
        volumes = config.mongo['volumes']
    elif databaseName == "mysql":
        ports = config.mysql['ports']
        volumes = config.mysql['volumes']
    elif databaseName == "postgres":
        ports = config.postgres['ports']
        volumes = config.postgres['volumes']
    else:
        return None
    if databaseNameConnection is None:
        containerName = databaseName + "_" + dockerImageId
    else:
        containerName = databaseNameConnection

    if system == "Unix Shell":
        file.write(
            "docker network ls|grep " + projectUuid + " > /dev/null || docker network create " + projectUuid + "\n")
        file.write(
            'docker ps -aq --filter "name=' + databaseNameConnection + '" | grep -q . &&  docker rm -f ' + databaseNameConnection + "\n")
        file.write(
            'docker ps -q --filter "name=' + databaseNameConnection + '" | grep -q . &&  docker rm -f ' + databaseNameConnection + "\n")

    if system == "windows":
        file.write(
            "docker network ls|Findstr " + projectUuid + " > $null || docker network create " + projectUuid + "\n")
        file.write(
            'docker ps -aq --filter "name=' + databaseNameConnection + '" | Findstr . &&  docker rm -f ' + databaseNameConnection + "\n")
        file.write(
            'docker ps -q --filter "name=' + databaseNameConnection + '" | Findstr . &&  docker rm -f ' + databaseNameConnection + "\n")

    file.write(
        "docker run -d --name " + containerName + " --network=" + projectUuid + " -p " + str(ports) + ":" + str(
            ports) + " -v " + databaseName + ":" + volumes + " " + databaseName + ":" + dockerImageId + "\n")

    if system == "windows":
        file.write("@ECHO Database is running...\n")
        file.write("PAUSE\n")

    if system == "Unix Shell":
        file.write("echo 'Database is running...'\n")
        file.write('read -p "Press ENTER to close" x\n')


    file.close()
