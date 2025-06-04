from random import randrange
import docker
import config
from settings import waitFromMessage


def buildMySqlImage(databaseParameters):
    ARG_ROOT_PASSWORD = databaseParameters["DBrootpass"]
    ARG_UserPASSWORD = databaseParameters["DBuserPass"]
    ARG_USER = databaseParameters["DBusername"]
    ARG_DATABASE = databaseParameters["DBdefaultDatabase"]

    return f"""\
# Use the official MySQL image from Docker Hub with the "latest" tag
FROM mysql:latest

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD={ARG_ROOT_PASSWORD}
ENV MYSQL_USER={ARG_USER}
ENV MYSQL_PASSWORD={ARG_UserPASSWORD}
ENV MYSQL_DATABASE={ARG_DATABASE}

# Expose MySQL port
EXPOSE 3306/tcp
"""


def buildMongoImage(databaseParameters):
    ARG_ROOT_PASSWORD = databaseParameters["DBrootpass"]
    ARG_DATABASE = databaseParameters["DBdefaultDatabase"]
    ARG_ROOT_USERNAME = databaseParameters["DBrootUser"]

    return f"""\
# Use the official MongDB image from Docker Hub with the "latest" tag
FROM mongo:latest

# Set environment variables for MongoDB
ENV MONGO_INITDB_ROOT_USERNAME={ARG_ROOT_USERNAME}
ENV MONGO_INITDB_ROOT_PASSWORD={ARG_ROOT_PASSWORD}
ENV MONGO_INITDB_DATABASE={ARG_DATABASE}

# Expose MongoDB port
EXPOSE 27017/tcp
"""


def buildPostgresImage(databaseParameters):
    ARG_DATABASE = databaseParameters["DBdefaultDatabase"]
    ARG_UserPASSWORD = databaseParameters["DBuserPass"]
    ARG_USER = databaseParameters["DBusername"]

    return f"""\
# Use the official Postgres image from Docker Hub with the "latest" tag
FROM postgres:latest

# Set environment variables for Postgres
ENV POSTGRES_USER={ARG_USER}
ENV POSTGRES_PASSWORD={ARG_UserPASSWORD}
ENV POSTGRES_DB={ARG_DATABASE}

# Expose Postgres port
EXPOSE 5432/tcp
"""


def buildDockerImageDatabase(myProjectFolder, databaseName, databaseParameters):
    # try:
    #     client = docker.from_env()
    # except Exception as e:
    #     print(str(e))
    #     raise Exception("Docker is not running")
    dockerfile_template = ""
    try:
        if databaseName == "MongoDB":
            dockerfile_template = buildMongoImage(databaseParameters)
        #     dockerfile = "dockerfile_mongo"
        #     buildargs = {"ARG_ROOT_USERNAME": databaseParameters["DBrootUser"],
        #                  "ARG_ROOT_PASSWORD": databaseParameters["DBrootpass"],
        #                  "ARG_DATABASE": databaseParameters["DBdefaultDatabase"]}

        elif databaseName == "MySQL":
            dockerfile_template = buildMySqlImage(databaseParameters)
        #     dockerfile = "dockerfile_mysql"
        #     buildargs = {"ARG_ROOT_PASSWORD": databaseParameters["DBrootpass"],
        #                  "ARG_PASSWORD": databaseParameters["DBuserPass"],
        #                  "ARG_DATABASE": databaseParameters["DBdefaultDatabase"]}

        elif databaseName == "PostgreSQL":
            dockerfile_template = buildPostgresImage(databaseParameters)
        #     dockerfile = "dockerfile_postgres"
        #     buildargs = {"ARG_PASSWORD": databaseParameters["DBuserPass"],
        #                  "ARG_USER": databaseParameters["DBusername"],
        #                  "ARG_DATABASE": databaseParameters["DBdefaultDatabase"]}
        else:
            dockerfile_template = ""

        # todo retirar
        # delete content from the Dockerfile
        open(myProjectFolder + "/DockerfileDatabase", "w").close()

        with open(myProjectFolder + "/DockerfileDatabase", "w") as dockerfile:
            dockerfile.write(dockerfile_template)

    except Exception as e:
        print(str(e))
        raise Exception(str(e))

    # dockerImageBuilt = client.images.build(path="configDockerDatabases", dockerfile=dockerfile, buildargs=buildargs,
    # tag=databaseName.lower() + ":" + str(number), rm=True)

    return dockerfile_template


def runDockerContainerDatabase(dockerImageId, networkName, databaseName, databaseNameConnection):
    try:
        client = docker.from_env()
    except Exception as e:
        print(str(e))
        raise Exception("Docker is not running")

##TODO alterar
    databaseImage = client.images.get(dockerImageId).tags[0]

    number = randrange(1000)

    if databaseName == "MongoDB":
        ports = config.mongo['ports']
        volumes = config.mongo['volumes']
        waitMessage = "MongoDB init process complete"

    elif databaseName == "MySQL":
        ports = config.mysql['ports']
        volumes = config.mysql['volumes']
        waitMessage = "InnoDB initialization has ended"

    elif databaseName == "PostgreSQL":
        ports = config.postgres['ports']
        volumes = config.postgres['volumes']
        waitMessage = "PostgreSQL init process complete"
    else:
        return None
    #if databaseNameConnection is None:
     #   databaseNameConnection = databaseName + "_" + str(number)

    container = client.containers.run(image=databaseImage, name=databaseNameConnection, detach=True,
                                      network=networkName, ports={str(ports) + '/tcp': ports},
                                      volumes=['./' + dockerImageId.replace(":", "_") + ':' + volumes])

    waitFromMessage(container, waitMessage)
    return container
