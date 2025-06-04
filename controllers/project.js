const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const StreamZip = require('node-stream-zip');
const axios = require('axios');
const fs = require('fs');
const tar = require('tar');
const path = require('path');

const {v4: uuidv4} = require('uuid');
const requestConfig = {
    headers: {
        Accept: 'application/zip',
    },
    responseType: 'arraybuffer',
}
const requestConfigAcceptAll = {
    headers: {
        Accept: '*/*',
    },
    responseType: 'arraybuffer',
}
const {
    addFilesToDatabase, createProject, getProject, getAllProjects,
    getPythonFilesByProjectDatabase, getFilesByProjectDatabase,
    getFoldersFromFolderDatabase, getFilesFromFolderDatabase,
    addFoldersToDatabase, getFoldersByProjectDatabase, deleteProject,
    addLanguagesToProjectDatabase, getLanguagesFromProject,
} = require("../models/project");

const {initializeSession} = require("../config/neo4j")
let env;
const myArgs = process.argv.slice(2);
if (myArgs.length > 0) {
    env = myArgs[0]
}
const config = require(__dirname + '/../config/config')[env];

function makeFolderRoot(projectUuid) {
    const repositoriesDirectory = "./repositories"
    if (!fs.existsSync(repositoriesDirectory)) {
        fs.mkdirSync(repositoriesDirectory);
    }
    const projectDirectory = repositoriesDirectory + "/" + projectUuid;

    if (!fs.existsSync(projectDirectory))
        fs.mkdirSync(projectDirectory);

    const projectFiles = projectDirectory + "/files";

    if (!fs.existsSync(projectFiles))
        fs.mkdirSync(projectFiles);

    if (!fs.existsSync("./extracted"))
        fs.mkdirSync("./extracted");

    if (!fs.existsSync(`./extracted/${projectUuid}`))
        fs.mkdirSync(`./extracted/${projectUuid}`);

    return projectFiles;
}

//see https://docs.figshare.com/
//figshare
//get all the information from a project curl -X GET "https://api.figshare.com/v2/articles/{article_id}"
//https://docs.figshare.com/#public_article


//download all the files from a project
//https://figshare.com/ndownloader/articles/20965759/versions/1 ---zipfile
//https://figshare.com/ndownloader/articles/<figshare doi>/versions/<version 1..*>

//get all the files from a project
//https://api.figshare.com/v2/articles/20965759/files ---list
//https://api.figshare.com/v2/articles/<doi>/files
//https://docs.figshare.com/#article_files


//https://zenodo.org/record/51908#.ZAj0WXbP1D-
//10.5281/zenodo.51908

//figshare
//https://figshare.com/articles/journal_contribution/Summarizing_Data_in_Python_with_Pandas/1041843
//https://doi.org/10.6084/m9.figshare.1041843.v3

async function getProjectFromRemoteRepository(projectUuid, projectFiles, bodyRequest) {
    let defaultBranchName = bodyRequest.defaultBranchName
    let projectLocation = bodyRequest.projectLocation
    let repositorySelected = bodyRequest.repositorySelected
    let requestResultArray = []

    let hasZipFile = false;

    if (repositorySelected === "GitHub") {
        requestResultArray.push(await axios.get(`https://github.com/${projectLocation}/archive/refs/heads/${defaultBranchName}.zip`, requestConfig))
    } else if (repositorySelected === "Figshare") {
        const regexpSize = /(?:[a-z]|.|:|\/)*10.6084\/m9.figshare.([0-9]+).v([0-9]+)/;
        const match = projectLocation.match(regexpSize);
        if (!match) {
            return null
        } else if (match.length !== 3) {
            return null
        } else {
            requestResultArray.push(await axios.get(`https://figshare.com/ndownloader/articles/${match[1]}/versions/${match[2]}`, requestConfig))
        }
    } else if (repositorySelected === "Zenodo") {
        const regexpSize = /(?:[a-z]|.|:|\/)*10.5281\/zenodo.([0-9]+)/;
        const match = projectLocation.match(regexpSize);
        if (!match) {
            return null
        } else if (match.length !== 2) {
            return null
        } else {
            let result = await axios.get(`https://zenodo.org/api/records/${match[1]}`)
            for (let file of result.data.files) {

                const downloadAllFiles = bodyRequest.downloadAllFiles

                const filesToDownloads = bodyRequest.files
                let downloadThisFile = true

                if (downloadAllFiles !== true) {
                    if (!Array.isArray(filesToDownloads))
                        return [];
                    if (!filesToDownloads.includes(file.filename))
                        downloadThisFile = false;
                }
                if (downloadThisFile) {
                    let resultFile = await axios.get(file.links.download, requestConfigAcceptAll)
                    console.log(file)
                    if (resultFile.headers["content-type"] === "application/zip" || resultFile.headers["content-type"] === "application/octet-stream") {
                        requestResultArray.push({
                            data: await axios.get(file.links.download, requestConfigAcceptAll),
                            filename: file.filename
                        })
                        hasZipFile = true;
                    } else {
                        await fs.writeFileSync(`${projectFiles}/${file.filename}`, resultFile.data)
                    }
                }
            }
        }

    }
    if (repositorySelected === "Zenodo" && hasZipFile === false) {
        return false
    } else {
        let filenameArray = []
        for (let zipFile of requestResultArray) {

            //let filename = "name" + new Date().getTime()+".zip"
            filenameArray.push(zipFile.filename)
            await fs.writeFileSync(`./extracted/${projectUuid}/${zipFile.filename}`, zipFile.data.data)
        }
        return filenameArray
    }
}
async function openAndExtractGZFile(projectUuid, projectFiles, fileOrProject) {
    await tar.x(
        {
            file: `./extracted/${projectUuid}/${fileOrProject.name}`,
            strip: 1,
            C: projectFiles
        })
    await fs.unlinkSync(`./extracted/${projectUuid}/${fileOrProject.name}`)
}
async function openAndExtractZipFile(projectUuid, projectFiles, fileOrProject) {

    let zip = new StreamZip.async({file: `./extracted/${projectUuid}/${fileOrProject.name}`});
    const entries = await zip.entries();
    const allEntities = []
    for (const entry of Object.values(entries)) {
        let rootEntity = entry.name.split("/")[0]
        allEntities.push(rootEntity)
    }
    const allEntitiesWithoutDuplicates = [...new Set(allEntities)]

    if (allEntitiesWithoutDuplicates.length === 1) {
        await zip.extract(allEntitiesWithoutDuplicates[0], `./extracted/${projectUuid}/`);
    } else {
        await zip.extract('', `./extracted/${projectUuid}/`);

    }
    await fs.unlinkSync(`./extracted/${projectUuid}/${fileOrProject.name}`)
    await zip.close();
}
async function addFilesAndFolderToProjectAux(extractedFolder, projectUuid, firstIteration, parentDirectoryKey, fileExtension) {

    let filesToAdd = []
    let foldersToAdd = []

    // list all files in the directory
    let myFileExtensionArray;
    try {
        const files = fs.readdirSync(extractedFolder)
        for (const file of files) {

            if (!file.endsWith(".zip")) {
                let stats = fs.statSync(extractedFolder + '/' + file);
                console.log("full path")
                let fullPath = extractedFolder + '/' + file
                let fullPathSplited = fullPath.split("./extracted/" + projectUuid + "/")

                console.log("stats")
                //console.log(stats)
                if (stats.isFile()) {
                    let fileInformation = {
                        name: file,
                        size: stats.size,
                        key: uuidv4(),
                        fullPath: fullPathSplited[1],
                        dateModified: new Date().toLocaleDateString()
                    }
                    myFileExtensionArray = file.split(".")
                    if (myFileExtensionArray.length > 1) {
                        fileExtension.push(myFileExtensionArray[1])
                    }
                    filesToAdd.push(fileInformation)

                } else if (stats.isDirectory() && file !== ".idea" && file !== "__pycache__") {
                    let folderInformation = {
                        name: file,
                        key: uuidv4(),
                        fullPath: fullPathSplited[1],
                        dateModified: new Date().toLocaleDateString()
                    }
                    foldersToAdd.push(folderInformation)
                }
            }
        }
        const session = initializeSession()
        let result

        if (filesToAdd.length > 0) {
            if (firstIteration) {
                result = await addFilesToDatabase(session, projectUuid, filesToAdd)
                console.log(typeof result)

            } else {
                result = await addFilesToDatabase(session, projectUuid, filesToAdd, parentDirectoryKey)
            }
            if (result.records.length === 0) {
                await session.rollback()
                return false
            } else {
                await session.commit()
                await session.close()
            }
        }

        if (foldersToAdd.length > 0) {
            const session = initializeSession()
            if (firstIteration) {
                console.log("_______________________")
                result = await addFoldersToDatabase(session, projectUuid, foldersToAdd)
            } else {
                result = await addFoldersToDatabase(session, projectUuid, foldersToAdd, parentDirectoryKey)
            }

            if (result.records.length === 0) {
                await session.rollback()
                return false

            } else {
                await session.commit()
                await session.close()

                for (const folderCreated of result.records[0]._fields) {
                    const myFolderInformation = folderCreated.properties

                    let myResult = await addFilesAndFolderToProjectAux(extractedFolder + '/' + folderCreated.properties.name, projectUuid, false, myFolderInformation, fileExtension)
                    if (!myResult)
                        return false;
                }
            }
        }
        return true
    } catch
        (err) {
        console.log(err)
        return false
    }
}
async function getContentFromFolderAux(projectUuid, key, firstIteration) {

    console.log("key: " + key)
    try {
        let date = new Date().toLocaleString();
        console.log(date)
        let items = []
        let myResult
        if (firstIteration) {
            myResult = await getFoldersByProjectDatabase(projectUuid)
            let myResult2 = await getFilesByProjectDatabase(projectUuid)
            let date2 = new Date().toLocaleString();
            console.log("date2")
            console.log(date2)
            myResult.records = myResult.records.concat(myResult2.records);
        } else {
            myResult = await getFoldersFromFolderDatabase(key)
            let myResult2 = await getFilesFromFolderDatabase(key)
            myResult.records = myResult.records.concat(myResult2.records);
        }
        let date3 = new Date().toLocaleString();
        console.log("date3")
        console.log(date3)

        if (myResult.records.length === 0) {
            return [];
        } else {
            for (let record of myResult.records) {
                for (let field of record._fields) {

                    if (field !== null) {
                        let nodeType = field.labels[0]
                        if (nodeType === "Folder") {
                            console.log("ciclo")
                            let resultObject = await getContentFromFolderAux(null, field.properties.key, false)

                            let folderResult = field.properties
                            folderResult.isDirectory = true
                            folderResult.items = resultObject

                            items.push(folderResult)
                        }
                        if (nodeType === "File") {
                            let fileResult = field.properties
                            fileResult.isDirectory = false
                            items.push(fileResult)
                        }
                    }
                }
            }
        }
        return items
    } catch (e) {
        throw e
    }
}
async function addLanguagesToProject(projectUuid, fileExtension) {

    const myProgrammingLanguages = await getLanguagesFromProject(projectUuid)

    let programmingLanguages = []
    if (fileExtension.includes("cpp") && !myProgrammingLanguages.includes("cPlusPlus"))
        programmingLanguages.push("cPlusPlus")

    if (fileExtension.includes("sh") && !myProgrammingLanguages.includes("shell"))
        programmingLanguages.push("shell")

    if ((fileExtension.includes("java") || fileExtension.includes("jar")) && !myProgrammingLanguages.includes("java"))
        programmingLanguages.push("java")

    if (fileExtension.includes("py") && !myProgrammingLanguages.includes("python"))
        programmingLanguages.push("python")


    const session1 = initializeSession()
    let result = await addLanguagesToProjectDatabase(session1, projectUuid, programmingLanguages)
    if (result.records.length === 0) {
        await session1.rollback()
        return false
    } else {
        await session1.commit()
        await session1.close()
        return true
    }
}
function deleteDirectory(directory) {
    //await fs.rmSync(`./deleteDirectory/${projectUuid}`, {recursive: true, force: true});

    // delete directory recursively
    fs.rm(`./extracted/${directory}`, {recursive: true, force: true}, err => {
        if (err)
            throw err;
        console.log(`./extracted/${directory} is deleted!`)
    })
}
async function addFilesAndFolderToProject(projectUuid) {
    console.log("inicio addFilesAndFolderToProject")
    let fileExtension = []
    let result = await addFilesAndFolderToProjectAux(`./extracted/${projectUuid}`, projectUuid, true, null, fileExtension)
    if (!result)
        throw "some error occurred";

    let result2 = await addLanguagesToProject(projectUuid, fileExtension)
    if (!result2)
        throw "some error occurred";

    console.log("fim addFilesAndFolderToProject")
    return result
}
function moveContent(projectUuid, projectFiles) {
    fs.readdir(`./extracted/${projectUuid}/`, (err, files) => {
        if (err) {
            console.error('Error reading source directory:', err);
            return;
        }

        // Loop through the files in the source directory
        files.forEach((file) => {
            const sourceFilePath = path.join(`./extracted/${projectUuid}/`, file);
            const destinationFilePath = path.join(projectFiles, file);

            // Move the file
            fs.rename(sourceFilePath, destinationFilePath, (err) => {
                err ? console.error(`Error moving ${file}:`, err) : console.log(`${file} moved successfully.`);
            });
        });
    });
}

module.exports = {
    async uploadRemoteProject(req, res) {
        console.log(req.params);
        let projectUuid = req.params.projectUuid;
        let bodyRequest = req.body

        if (!projectUuid) {
            return res.status(400).send({message: 'projectUuid is required'});
        } else {
            try {
                if (bodyRequest.repositorySelected === "GitHub" && (bodyRequest.projectLocation === "null" || bodyRequest.defaultBranchName === "null")) {
                    return res.status(404).send({
                        message: 'The location of the Git Project was not provided'
                    });
                } else if (bodyRequest.repositorySelected !== "GitHub" && (bodyRequest.projectLocation === "null")) {
                    return res.status(404).send({
                        message: 'The location of the Project was not provided'
                    });
                }

                const projectFiles = makeFolderRoot(projectUuid);
                let resultArray = await getProjectFromRemoteRepository(projectUuid, projectFiles, bodyRequest)
                if (resultArray === null) {
                    return res.status(404).send({
                        message: 'An error had occurred'
                    })
                } else if (resultArray === false) {
                    //project without zip files
                    return res.status(200).send({
                        status: true,
                        message: `${bodyRequest.repositorySelected} project was successfully uploaded`
                    })
                } else {
                    for (let zipFileName of resultArray) {
                        let fileOrProject = {
                            name: zipFileName
                        }
                        if (zipFileName.endsWith(".gz") || zipFileName.endsWith(".tar")) {
                            await openAndExtractGZFile(projectUuid, projectFiles, fileOrProject)
                        } else if (zipFileName.endsWith(".zip")) {
                            await openAndExtractZipFile(projectUuid, projectFiles, fileOrProject)
                        }
                        try {
                            await addFilesAndFolderToProject(projectUuid)
                        } catch (e) {
                            return res.status(500).send({
                                status: false,
                                message: e.message
                            })

                        }
                    }
                    return res.status(200).send({
                        status: true,
                        message: `${bodyRequest.repositorySelected} project was successfully uploaded`
                    })
                }
            } catch (err) {
                return res.status(500).send({
                    status: false,
                    message: err.message
                })
            }
        }
    },

    async uploadProject(req, res) {
        console.log(req.params);
        let projectUuid = req.params.projectUuid;

        if (!projectUuid) {
            return res.status(400).send({message: 'projectUuid is required'});
        } else {
            try {
                if (!req.files) {
                    return res.status(404).send({
                        message: 'File not provided'
                    });
                } else {
                    const projectFiles = makeFolderRoot(projectUuid);
                    let fileOrProject = req.files.file
                    let result
                    await fileOrProject.mv(`./extracted/${projectUuid}/${fileOrProject.name}`);

                    if (fileOrProject.mimetype === "application/x-zip-compressed" || fileOrProject.mimetype === "application/zip") {
                        await openAndExtractZipFile(projectUuid, projectFiles, fileOrProject)
                        result = await addFilesAndFolderToProject(projectUuid)

                        moveContent(projectUuid, projectFiles);
                        //deleteDirectory(projectUuid);
                    } else {
                        result = await addFilesAndFolderToProject(projectUuid)
                        moveContent(projectUuid, projectFiles);
                        //deleteDirectory(projectUuid);
                    }

                    if (result) {
                        let message
                        if (fileOrProject.mimetype === "application/x-zip-compressed") {
                            message = 'Project was uploaded'
                        } else {
                            message = "File was uploaded"
                        }
                        console.log("envio")
                        return res.status(200).send({
                            status: true,
                            message: message
                        })
                    } else {
                        return res.status(404).send({
                            message: 'An error had occurred'
                        })
                    }
                }
            } catch (err) {
                return res.status(500).send({
                    status: false,
                    message: err.message
                })
            }
        }
    },

    async uploadFile(req, res) {
        console.log(req.params);
        let projectUuid = req.params.projectUuid;
        let bodyRequest = req.body
        if (!projectUuid) {
            return res.status(400).send({message: 'projectUuid is required'});
        } else {
            try {
                if (!bodyRequest.parentDirectory || !bodyRequest.fileInformation) {
                    return res.status(400).send({
                        message: 'ParentDirectory or fileInformation is not provided'
                    });
                } else if (!req.files)
                    return res.status(400).send({
                        message: 'No file uploaded'
                    });

                let parentDirectoryObject = JSON.parse(bodyRequest.parentDirectory)
                let fileInformation = JSON.parse(bodyRequest.fileInformation)
                const file = req.files.file

                const projectFiles = makeFolderRoot(projectUuid);

                const session = initializeSession()
                let result;
                if (parentDirectoryObject.path === "" && parentDirectoryObject.key === "") {
                    result = await addFilesToDatabase(session, projectUuid, [fileInformation])
                } else {
                    result = await addFilesToDatabase(session, projectUuid, [fileInformation], parentDirectoryObject)
                }
                if (result.records.length === 0) {
                    return res.status(404).send({
                        message: "There is not a project with uuid = " + projectUuid + ""
                    })
                } else {
                    await file.mv(projectFiles + "/" + fileInformation.fullPath);
                    await session.commit()
                    await session.close()

                    let result2 = await addLanguagesToProject(projectUuid, fileInformation.fullPath)
                    if (!result2)
                        return res.status(500).send({
                            message: "The programming languages are not added"
                        });

                    return res.status(200).send({
                        status: true,
                        message: 'File was uploaded'
                    })
                }
            } catch
                (err) {
                return res.status(500).send({
                    message: err.message
                });
            }
        }
    },

    async addFolder(req, res) {
        console.log(req.params);
        let projectUuid = req.params.projectUuid;

        if (!projectUuid)
            return res.status(400).send({message: 'projectUuid is required'});

        try {
            if (!req.body.parentDirectory || !req.body.folderInformation) {
                return res.status(400).send({
                    message: 'ParentDirectory or folderInformation is not provided'
                });
            } else {
                let parentDirectoryObject = JSON.parse(req.body.parentDirectory)
                let folderInformation = JSON.parse(req.body.folderInformation)
                const projectFiles = makeFolderRoot(projectUuid);

                const session = initializeSession()
                let result;
                if (parentDirectoryObject.path === "" && parentDirectoryObject.key === "") {
                    result = await addFoldersToDatabase(session, projectUuid, [folderInformation])
                } else {
                    result = await addFoldersToDatabase(session, projectUuid, [folderInformation], parentDirectoryObject)
                }
                if (result.records.length === 0) {
                    return res.status(400).send({
                        message: "There is not a project with uuid = " + projectUuid + ""
                    })
                } else {

                    if (!fs.existsSync(projectFiles + "/" + folderInformation.fullPath))
                        fs.mkdirSync(projectFiles + "/" + folderInformation.fullPath);

                    await session.commit()
                    await session.close()

                    return res.status(200).send({
                        status: true,
                        message: 'Folder was created'
                    })
                }
            }
        } catch (e) {
            return res.status(500).send({
                message: e.message
            })
        }
    },

    async create(req, res) {
        console.log(req.body);
        const projectName = req.body.name;
        const projectDescription = req.body.description;

        if (!projectName)
            return res.status(400).send({message: 'Title is required'});
        try {
            const session = initializeSession()
            let result = await createProject(session, projectName, projectDescription)
            if (result.length === 0) {
                await session.rollback()
                return res.status(404).send({
                    message: 'Project was not created'
                })
            } else {
                await session.commit()
                await session.close()

                return res.status(201).send({
                    projectUuid: result[0],
                    message: 'Project was created'
                })
            }
        } catch (e) {
            return res.status(500).send({
                message: e.message
            })
        }
    },

    async getById(req, res) {
        const projectUuid = req.params.projectUuid
        try {
            let date = new Date()
            let result = await getProject(projectUuid)
            let date2 = new Date()
            let diff = date2.getTime() - date.getTime();
            console.log("difftime get:" + diff); // 2022-06-17T11:06:50.369Z

            if (result.records.length === 0) {
                return res.status(404).send({
                    message: "There is not a project with uuid = " + projectUuid + "",
                });
            } else {
                const projectNode = result.records[0]._fields[0].properties
                return res.status(200).send(projectNode);
            }
        } catch (e) {
            return res.status(400).send({message: e.message})
        }
    },

    async getFoldersByProject(req, res) {
        const projectUuid = req.params.projectUuid
        try {
            let items = []
            items = await getContentFromFolderAux(projectUuid, null, true)
            return res.status(200).send(items);
        } catch
            (e) {
            return res.status(400).send({message: e.message})
        }
    },

    async getProgrammingLanguages(req, res) {
        const projectUuid = req.params.projectUuid
        if (!projectUuid) {
            return res.status(400).send({message: 'projectUuid is required'});
        } else {
            try {
                const myProgrammingLanguages = await getLanguagesFromProject(projectUuid)
                return res.status(200).send(myProgrammingLanguages);
            } catch (e) {
                return res.status(400).send({message: e.message})
            }
        }
    },

    async getAll(req, res) {
        try {
            let result = await getAllProjects()
            return res.status(200).send(result);
        } catch (e) {
            return res.status(400).send({message: e.message})
        }
    },

    async delete(req, res) {
        console.log(req.params.projectUuid)
        try {
            const projectUuid = req.params.projectUuid;
            if (!projectUuid)
                return res.status(404).send({
                    message: 'projectUuid is required',
                });

            const session = initializeSession()
            let result = await deleteProject(session, projectUuid)

            await session.commit()
            await session.close()

            console.log(result)
            //delete folder locally
            const repositoriesDirectory = "./repositories"
            const projectDirectory = repositoriesDirectory + "/" + projectUuid;

            fs.rmSync(projectDirectory, {recursive: true, force: true});
            return res.status(200).send({message: 'The project with Uuid=' + projectUuid + " was deleted"});
        } catch (e) {
            return res.status(400).send({message: e.message})
        }
    },

    async getPythonFilesByProject(req, res) {
        const projectUuid = req.params.projectUuid
        try {
            let myResult = await getPythonFilesByProjectDatabase(projectUuid)
            return res.status(200).send(myResult);
        } catch (err) {
            return res.status(500).send({
                message: err.message
            })
        }
    },

    async IsLogged(req, res) {
        return res.status(200).send({message: 'isLogged'})
    },

    async update(req, res) {
        const user = await Users.findByPk(req.params.id);
        if (!user) {
            return res.status(404).send({
                message: 'Users Not Found',
            });
        }
        try {
            await user
                .update({
                    firstname: req.body.firstname || user.firstname,
                    lastname: req.body.lastname || user.lastname,
                    updatedAt: new Date(),
                    createdat: user.createdat,
                    password: req.body.password || user.password
                })
            return res.status(200).send(user)
        } catch (e) {
            return res.status(400).send({message: e.message})
        }
    },
    async login(req, res) {
        console.log(req.body);
        const username = req.body.username;
        const password = req.body.password;

        if (!username || !password) {
            return res.status(400).send({message: 'Username and password are required'});
        }
        const user = await Users.findOne({where: {username: username}})
        if (!user) {
            return res.status(400).send({message: 'Username not exists'});
        }
        const userPassword = user.getDataValue('password')

        bcrypt.compare(password, userPassword, function (err, isMatch) {
            if (err) {
                throw err
            } else if (!isMatch) {
                return res.status(401).send({message: 'Username or password are wrong'})
            } else {

                const token = jwt.sign({id: user.id}, config.secret, {
                    expiresIn: 3600 // expires in 1 hour
                });
                const newUser = Object.assign(user.toJSON(), {token: token});
                const body = Object.assign({user: newUser}, {message: 'Successful login'});

                return res.status(200).send(body);
            }
        })
    }
}