const express = require('express');
const router = express.Router();

const neo4j = require('neo4j-driver');


function formatResponse(resultObj) {
    const result = [];
    if (resultObj.records.length > 0) {
        resultObj.records.map(record => {
            result.push(record._fields[0].properties);
        });
    }
    //resultObj.records.map(record => record.get('language').properties);
    return result;
}/*
router.post('/', async function(req, res) {
    const { id, name, email } = req.body;
    if (!id || id < 1 || !name || !email) {
        return res.status(400).send('Invalid Inputs');
    }
    const query = `CREATE (n:Users {id:$id, name:$name, email: $email}) RETURN n`;
    const params = {
        id: parseInt(id),
        name,
        email
    };
    const resultObj = await graphDBConnect.executeCypherQuery(query, params);
    const result = formatResponse(resultObj);
    res.send(result);
});
*/
router.get('/', async function(req, res) {
/*    const query = 'MATCH (n:Users) RETURN n LIMIT 100';
    const params = {};
    const resultObj = await graphDBConnect.executeCypherQuery(query, params);
    const result = formatResponse(resultObj);
    res.send(result);*/
    res.send({})
});


router.get('/create', async function(req, res) {
/*    const driver = neo4j.driver("neo4j://localhost:7687", neo4j.auth.basic("neo4j", "test"));

    const session = driver.session()
    const personName = 'Alice'

    try {
        const result = await session.run(
            'CREATE (a:Person {name: $name}) RETURN a',
            {name: personName}
        )

        const singleRecord = result.records[0]
        const node = singleRecord.get(0)

        console.log(node.properties.name)
    } finally {
        await session.close()
        res.send({})

    }

// on application exit:
    await driver.close()*/
});
/*
router.get('/:id', async function(req, res) {
    const { id } = req.params;
    const query = 'MATCH (n:Users {id: $id}) RETURN n LIMIT 100';
    const params = { id: parseInt(id) };
    const resultObj = await graphDBConnect.executeCypherQuery(query, params);
    const result = formatResponse(resultObj);
    res.send(result);
});

router.patch('/:id', async function(req, res) {
    const { id } = req.params;
    const { name, email } = req.body;
    let strName = name ? ` n.name = '${name}' ` : '';
    let strEmail = email ? ` n.email = '${email}' ` : '';
    if (strName && strEmail) {
        strEmail = ',' + strEmail;
    }
    const query = `MATCH (n:Users {id: $id}) SET ${strName} ${strEmail} RETURN n`;
    const params = { id: parseInt(id) };
    const resultObj = await graphDBConnect.executeCypherQuery(query, params);
    const result = formatResponse(resultObj);
    res.send(result);
});
router.delete('/:id', async function(req, res) {
    const { id } = req.params;
    const query = 'MATCH (n:Users {id: $id}) DELETE n';
    const params = { id: parseInt(id) };
    const resultObj = await graphDBConnect.executeCypherQuery(query, params);
    res.send('Delete success');
});
*/

module.exports = router;