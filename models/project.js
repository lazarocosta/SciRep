const {v4: uuidv4} = require('uuid');
const {initializeSession} = require("../config/neo4j");
module.exports = {
    async createProject(session, name, description) {
        let uuid = uuidv4();
        let result = await session.run('CREATE (p:Project {name: $name, description:$description, uuid:$uuid}) ' +
            'RETURN p', {
            name: name,
            description: description,
            uuid: uuid,
        })
        return result.records.map(record => record.get('p').properties.uuid);
    },

    async getProject(uuid) {
        const session = initializeSession()
        let x = await session.run('MATCH (p:Project) WHERE p.uuid=$uuid RETURN p', {
            uuid: uuid,
        })
        await session.close()
        return x
    },

    async getPythonFilesByProjectDatabase(uuid) {
        const session = initializeSession()
        const pythonFilesResult = await session.run('MATCH (p:Project)-[:HAS_PYTHON_FILE]->(file) ' +
            'WHERE p.uuid=$uuid ' +
            'return file', {
            uuid: uuid,
        })
        await session.close()
        return pythonFilesResult.records.map(record => record.get('file').properties);
    },

    async getFilesByProjectDatabase(uuid) {
        const session = initializeSession()
        let result = await session.run('MATCH (p:Project)-[:HAS_FILE ]->(file) ' +
            'WHERE p.uuid=$uuid ' +
            'return file', {
            uuid: uuid,
        })
        await session.close()
        return result
    },

    async getFoldersByProjectDatabase(uuid) {
        const session = initializeSession()
        let result = await session.run('MATCH (p:Project)-[:HAS_FOLDER]->(folder) ' +
            'WHERE p.uuid=$uuid ' +
            //'optional MATCH (p)-[:HAS_FOLDER]->(folder) ' +
            //' MATCH (p)-[:HAS_FILE]->(file) ' +
            'return folder ', {
            uuid: uuid,
        })
        await session.close()
        return result
    },

    async getFoldersFromFolderDatabase(key) {
        const session = initializeSession()

        let result = await session.run('MATCH (folder:Folder)-[:HAS_FOLDER]->(f) ' +
            ' WHERE folder.key=$key ' +
            'return f ', {
            key: key,
        })
        await session.close()
        return result
    },

    async getFilesFromFolderDatabase(key) {
        const session = initializeSession()

        let result = await session.run('MATCH (folder:Folder)-[:HAS_FILE]->(file) ' +
            'WHERE folder.key=$key ' +
            'return file ', {
            key: key,
        })
        await session.close()
        return result
    },

    async getAllProjects() {
        const session = initializeSession()
        const projectsResult = await session.run('MATCH (p:Project) SET p.uuid = p.uuid ' +
            'RETURN p LIMIT 25', {})
        await session.close()
        return projectsResult.records.map(record => record.get('p').properties);
    },

    async addLanguagesToProjectDatabase(session, projectUuid, programmingLanguages) {
        function aux() {
            let myParameters = {}
            let languageIndex = 0
            let myQuery = 'MATCH (p:Project) WHERE p.uuid= $projectUuid '
            myParameters["projectUuid"] = projectUuid;

            for (let myLanguage of programmingLanguages) {
                let language = 'language' + languageIndex
                myQuery += 'CREATE (L' + languageIndex + ':Language $' + language + ') ';
                myQuery += 'CREATE (p)-[:HAS_LANGUAGE]->(L' + languageIndex + ') ';

                myParameters[language] = {
                    "name": myLanguage
                };
                languageIndex++
            }
            return {
                parameters: myParameters,
                query: myQuery
            }
        }

        let result = aux()

        return await session.run(result["query"] + 'return p',
            result["parameters"]
        )
    },

    async getLanguagesFromProject(projectUuid) {
        const session = initializeSession()
        const projectLanguages = await session.run('MATCH (p:Project)-[:HAS_LANGUAGE]->(language) ' +
            'WHERE p.uuid=$uuid ' +
            'return language ', {
            uuid: projectUuid
        })
        await session.close()
        return projectLanguages.records.map(record => record.get('language').properties.name);
    },

    async addFilesToDatabase(session, projectUuid, files, parentDirectoryObject = null) {
        function aux() {
            let myParameters = {}
            let fileIndex = 0
            let myQuery = 'MATCH (p:Project) WHERE p.uuid= $projectUuid '
            myParameters["projectUuid"] = projectUuid;

            if (parentDirectoryObject !== null) {
                myQuery += 'MATCH (folder:Folder {key:$sourceKey}) ';
                myParameters["sourceKey"] = parentDirectoryObject.key;
            }

            for (let file of files) {
                let content = 'content' + fileIndex
                myQuery += 'CREATE (f' + fileIndex + ':File $' + content + ') ';

                if (parentDirectoryObject !== null) {
                    myQuery += 'CREATE (folder)-[:HAS_FILE]->(f' + fileIndex + ') ';
                } else
                    myQuery += 'CREATE (p)-[:HAS_FILE]->(f' + fileIndex + ') ';

                if (file.name.endsWith(".py") && file.name !== "__init__.py") {
                    myQuery += 'CREATE (p)-[:HAS_PYTHON_FILE]->(f' + fileIndex + ') '
                }
                myParameters[content] = file;
                fileIndex++
            }

            return {
                parameters: myParameters,
                query: myQuery
            }
        }

        let result = aux()

        return await session.run(result["query"] + 'return p',
            result["parameters"]
        )
    },

    async addFoldersToDatabase(session, projectUuid, folders, parentDirectoryObject = null) {
        function aux() {
            let myParameters = {}
            let folderIndex = 0
            let myQuery = 'MATCH (p:Project) WHERE p.uuid= $projectUuid '
            myParameters["projectUuid"] = projectUuid;
            let foldersCreated = ""

            if (parentDirectoryObject !== null) {
                myQuery += 'MATCH (folderSource:Folder) WHERE folderSource.key= $keySource '
                myParameters["keySource"] = parentDirectoryObject.key;
            }

            for (let folder of folders) {

                let content = 'content' + folderIndex
                myQuery += 'CREATE (f' + folderIndex + ':Folder $' + content + ') ';
                //'CREATE (p)-[:HAS_THIS_FOLDER]->(f' + folderIndex + ') ';
                if (parentDirectoryObject !== null) {
                    myQuery += 'CREATE (folderSource)-[:HAS_FOLDER]->(f' + folderIndex + ') ';
                } else
                    myQuery += 'CREATE (p)-[:HAS_FOLDER]->(f' + folderIndex + ') ';

                myParameters[content] = folder;

                if (folderIndex === 0) {
                    foldersCreated += "f" + folderIndex
                } else {
                    foldersCreated += ",f" + folderIndex
                }
                folderIndex++
            }

            return {
                parameters: myParameters,
                query: myQuery,
                foldersCreated: foldersCreated
            }
        }

        let result = aux()

       return  await session.run(result["query"] + 'return ' + result["foldersCreated"],
            result["parameters"]
        )
    },

    async deleteProjectFiles(session, projectUuid) {
        return await session.run(
            'MATCH (p:Project) WHERE p.uuid= $projectUuid ' +
            'MATCH (p)-[:HAS_FILE]->(f:File) ' +
            'Detach Delete f',
            {projectUuid: projectUuid}
        )
    },

    async deleteProjectFolders(session, projectUuid) {
        return await session.run(
            'MATCH (p:Project) WHERE p.uuid= $projectUuid ' +
            'MATCH (p)-[:HAS_FOLDER]->(f:FOLDER) ' +
            'Detach Delete f',
            {projectUuid: projectUuid}
        )
    },

    async deleteProject(session, projectUuid) {
        return await session.run(
            'MATCH (project:Project) WHERE project.uuid= $projectUuid ' +
            'optional MATCH (project)-[:HAS_FOLDER]->(folder:FOLDER) ' +
            'optional MATCH (project)-[:HAS_FILE]->(file:File) ' +
            'Detach Delete folder, file, project',
            {projectUuid: projectUuid}
        )
    },
}