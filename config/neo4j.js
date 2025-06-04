const neo4j = require("neo4j-driver");
env ="development"
const config = require(__dirname + './../config/config.js')[env];


module.exports = {
    initializeSession() {
        const driver = neo4j.driver(config.dbHost, neo4j.auth.basic(config.dbUser, config.dbPass), {disableLosslessIntegers: true});
        const session = driver.session()
        return session.beginTransaction();
    }
}
