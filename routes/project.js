const project = require('../controllers/project');
const verifyToken = require('../controllers/verifyToken');

const express = require('express');
const router = express.Router();

router.post('/', verifyToken, project.create);
router.post('/:projectuuid/folder', verifyToken, project.addFolder);

router.get('/:projectuuid/programmingLanguages', verifyToken, project.getProgrammingLanguages);
router.get('/:projectuuid/pythonfiles', verifyToken, project.getPythonFilesByProject);
router.get('/:projectuuid/folders', verifyToken, project.getFoldersByProject);
router.delete('/:projectuuid', verifyToken, project.delete);
router.post('/:projectuuid/uploadfile', verifyToken, project.uploadFile);
router.post('/:projectuuid/uploadproject', verifyToken, project.uploadProject);
router.post('/:projectuuid/uploadgitproject', verifyToken, project.uploadRemoteProject);
router.post('/:projectuuid/addfolder', verifyToken, project.addFolder);




module.exports = router;

