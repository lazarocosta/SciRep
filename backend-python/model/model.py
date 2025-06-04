from neo4j import GraphDatabase

neo4jURI = "neo4j://localhost:7687"
AUTH = ("neo4j", "test1234")


def startsNeo4JConnection():
    return GraphDatabase.driver(neo4jURI, auth=AUTH)


def deleteSessionsFromDatabase(containersList):
    containersToDelete = ''
    for idx, container in enumerate(containersList):
        print(idx, container)
        if idx > 0:
            containersToDelete += ' OR  '
        containersToDelete += "c.container_id ='" + container + "'"

    def deleteSessionsFromDatabaseAux(tx):
        tx.run("MATCH (c:Container) WHERE " + containersToDelete +
               " DETACH DELETE c")

    driver = startsNeo4JConnection()

    with driver.session() as session:
        session.write_transaction(deleteSessionsFromDatabaseAux)

    driver.close()
    return True


def addSessionToDatabase(projectUuid, containerId):
    def createSessionRelationship(tx, projectUuid, containerId):
        tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
               "CREATE (c:Container {container_id: $containerId}) "
               "CREATE (p)-[:HAS_SESSION]->(c)",
               projectUuid=projectUuid, containerId=containerId)

    driver = startsNeo4JConnection()

    with driver.session() as session:
        session.write_transaction(createSessionRelationship, projectUuid, containerId)

    driver.close()
    return True


def getFileNamedAs(projectUuid, filename):
    def getRequerimentsFileAux(tx, projectUuid):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
                          "MATCH (p)-[:HAS_FILE]->(file:File {name: $name}) "
                          "RETURN file.key as key",
                          projectUuid=projectUuid, name=filename)
        return [record["key"] for record in sessions]

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.read_transaction(getRequerimentsFileAux, projectUuid)

    driver.close()
    return sessions


def getSessions(projectUuid):
    def getSessionsAux(tx, projectUuid):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
                          "MATCH (p)-[:HAS_SESSION]->(Container) "
                          "RETURN Container.container_id as containerId",
                          projectUuid=projectUuid)
        return [record["containerId"] for record in sessions]

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.read_transaction(getSessionsAux, projectUuid)

    driver.close()
    return sessions


def addExecutioToDatabase(projectUuid,configurationName,dataToAdd):
    def addExecutioToDatabaseAux(tx,projectUuid,dataToAdd, configurationName):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
                          "MATCH (c:Configure) WHERE c.configurationName =$configurationName "
                          "CREATE (e:Execution $dataToAdd) "
                          "CREATE (p)-[:HAS_EXECUTION]->(e) "
                          "CREATE (e)-[:HAS_CONFIGURATION]->(c) "
                          "RETURN e as result",
                          configurationName=configurationName,
                          dataToAdd=dataToAdd,
                          projectUuid=projectUuid)
        result = [record["result"] for record in sessions]
        return result[0]

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.write_transaction(addExecutioToDatabaseAux,projectUuid,dataToAdd, configurationName)

    driver.close()
    return sessions


def getConfiguration(projectUuid):
    def getConfigurationAux(tx, projectUuid):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
                          "MATCH (p)-[:HAS_CONFIGURATION]->(Configuration) "
                          "OPTIONAL MATCH (Configuration)-[:HAS_DATABASE]->(database:Database)"
                          "RETURN Configuration as configuration, database as database",
                          projectUuid=projectUuid)
        data = {}
        for record in sessions.data():
            id = record['configuration']['dockerImageID']
            configuration = {str(id): record["configuration"]}
            configuration[id]['database'] = record["database"]
            data = {**data, **configuration}
        return data

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.read_transaction(getConfigurationAux, projectUuid)

    driver.close()
    return sessions


def hasSession(projectUuid, containerId):
    def getSessionAux(tx, projectUuid, containerId):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
                          "MATCH (c:Container) WHERE c.container_id =$containerId "
                          "MATCH (p)-[r:HAS_SESSION]->(c) "
                          "RETURN COUNT(r) as result",
                          projectUuid=projectUuid, containerId=containerId)

        result = [record["result"] for record in sessions]
        return result[0]

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.read_transaction(getSessionAux, projectUuid, containerId)

    driver.close()
    return sessions


def addConfigurationToDatabase(projectUuid, configure):
    def addConfigurationAux(tx, myprojectUuid, myconfigure):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid =$projectUuid "
                          "CREATE (c:Configure $source_id) "
                          "CREATE (p)-[:HAS_CONFIGURATION]->(c) "
                          "RETURN c as result",
                          projectUuid=myprojectUuid, source_id=configure, configuration=myconfigure)
        # sessions = tx.run(
        #     "CREATE (a:Configure {configurationName: $configurationName, operatingSytem: $operatingSytem, dockerImageID: $dockerImageID})",
        #     configurationName=configurationName,operatingSytem =operatingSytem, dockerImageID= dockerImageID )

        result = [record["result"] for record in sessions]
        return result[0]

    driver = startsNeo4JConnection()
    with driver.session() as session:


        node = session.write_transaction(addConfigurationAux, projectUuid, configure)

    driver.close()
    return node


def addDatabaseConfigurationToDatabase(configurationNode, configure):
    def addConfigurationAux(tx, configurationNode, configure):
        # MATCH (s) WHERE ID(s) =15  DETACH DELETE s

        sessions = tx.run("MATCH (s) WHERE ID(s) = $nodeId "
                          "CREATE (d:Database $source_id) "
                          "CREATE (s)-[:HAS_DATABASE]->(d) "
                          "RETURN d as result",
                          nodeId=configurationNode, source_id=configure)
        # sessions = tx.run(
        #     "CREATE (a:Configure {configurationName: $configurationName, operatingSytem: $operatingSytem, dockerImageID: $dockerImageID})",
        #     configurationName=configurationName,operatingSytem =operatingSytem, dockerImageID= dockerImageID )

        result = [record["result"] for record in sessions]
        return result[0]

    driver = startsNeo4JConnection()
    with driver.session() as session:

        node = session.write_transaction(addConfigurationAux, configurationNode, configure)

    driver.close()
    return node


def getPythonFiles(projectUuid):
    def getPythonFilesAux(tx, projectUuid):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid=$projectUuid " +
                          "optional MATCH (p)-[:HAS_PYTHON_FILE ]->(file) " +
                          "return file.fullPath as fullPath",
                          projectUuid=projectUuid)

        result = [record["fullPath"] for record in sessions]
        return result

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.read_transaction(getPythonFilesAux, projectUuid)

    driver.close()
    return sessions


def getProjectFolders(projectUuid):
    def getProjectFoldersAux(tx, projectUuid):
        sessions = tx.run("MATCH (p:Project) WHERE p.uuid=$projectUuid " +
                          "optional MATCH (p)-[:HAS_THIS_FOLDER ]->(folder) " +
                          "return folder.fullPath as fullPath",
                          projectUuid=projectUuid)

        result = [record["fullPath"] for record in sessions]
        return result

    driver = startsNeo4JConnection()
    with driver.session() as session:
        sessions = session.read_transaction(getProjectFoldersAux, projectUuid)

    driver.close()
    return sessions
