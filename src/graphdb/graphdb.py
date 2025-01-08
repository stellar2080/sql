from neo4j import GraphDatabase

from src.graphdb.graphdb_base import GraphDB_Base


def create_node_tx(tx, node_type, name):
    cypher = f"CREATE (a:{node_type} {{name:'{name}'}})"
    tx.run(cypher)

def create_relation_tx(tx, relation_type, type_a, name_a, type_b, name_b):
    cypher = f"MATCH (a:{type_a} {{name:'{name_a}'}}), (b:{type_b} {{name:'{name_b}'}}) CREATE (a)-[:{relation_type}]->(b)"
    tx.run(cypher)

def get_nodes_tx(tx, node_type=None, name=None):
    if node_type == "Node":
        if name:
            cypher = f"MATCH (a) WHERE a.name='{name}' RETURN a"
        else:
            cypher = "MATCH (a) RETURN a"
    else:
        if name:
            cypher = f"MATCH (a:{node_type}) WHERE a.name='{name}' RETURN a"
        else:
            cypher = f"MATCH (a:{node_type}) RETURN a"

    result = tx.run(cypher)
    for record in result:
        node = record['a']
        print("[Node]")
        print("Labels:", list(node.labels) , "\nName:", node['name'])
        print("-"*20)

    return result

def get_relation_tx(tx, relation_type=None):
    if relation_type == "Relation":
        cypher = "MATCH (a)-[r]->(b) RETURN a, r, b"
    else:
        cypher = f"MATCH (a)-[r:{relation_type}]->(b) RETURN a, r, b"

    result = tx.run(cypher)
    for record in result:
        a = record['a']
        b = record['b']
        r = record['r']
        print("[Relation]")
        print(a['name'], "-[", r.type, "]->", b['name'])
        print("-" * 20)

    return result


def del_nodes_tx(tx, node_type=None, name=None):
    if node_type == "Node":
        if name:
            cypher = f"MATCH (a) WHERE a.name = '{name}' DETACH DELETE a"
        else:
            cypher = "MATCH (a) DETACH DELETE a"
    else:
        if name:
            cypher = f"MATCH (a:{node_type}) WHERE a.name = '{name}' DETACH DELETE a"
        else:
            cypher = f"MATCH (a:{node_type}) DETACH DELETE a"

    tx.run(cypher)

def del_relation_tx(tx, relation_type=None):
    if relation_type == "Relation":
        cypher = "MATCH (a)-[r]->(b) DELETE r"
    else:
        cypher = f"MATCH (a)-[r:{relation_type}]->(b) DELETE r"

    tx.run(cypher)

C_FUNC_LIST = {
    "Word": create_node_tx,
    "Middle": create_node_tx,
    "Column": create_node_tx,

    "Add": create_relation_tx,
    "Sub": create_relation_tx,
    "Mul": create_relation_tx,
    "Div": create_relation_tx
}

G_FUNC_LIST = {
    "Word": get_nodes_tx,
    "Middle": get_nodes_tx,
    "Column": get_nodes_tx,
    "Node": get_nodes_tx,

    "Add": get_relation_tx,
    "Sub": get_relation_tx,
    "Mul": get_relation_tx,
    "Div": get_relation_tx,
    "Relation": get_relation_tx,
}

D_FUNC_LIST = {
    "Word": del_nodes_tx,
    "Middle": del_nodes_tx,
    "Column": del_nodes_tx,
    "Node": del_nodes_tx,

    "Add": del_relation_tx,
    "Sub": del_relation_tx,
    "Mul": del_relation_tx,
    "Div": del_relation_tx,
    "Relation": del_relation_tx,
}

class GraphDB(GraphDB_Base):
    def __init__(self,config):
        super().__init__(config)
        uri = config.get("graphdb_uri","bolt://localhost:7687")
        username = config.get("graphdb_username","neo4j")
        password = config.get("graphdb_password","12345678")
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def create_node(self, node_type, name):
        func = C_FUNC_LIST[node_type]
        if not func:
            raise Exception("Node_type not found")
        with self.driver.session() as session:
            session.execute_write(func, node_type, name)
        self.driver.close()

    def create_relation(self, relation_type, node_type_a, name_a, node_type_b, name_b):
        func = C_FUNC_LIST[relation_type]
        if not func:
            raise Exception("Relation_type not found")
        with self.driver.session() as session:
            session.execute_write(func, relation_type, node_type_a, name_a, node_type_b, name_b)
        self.driver.close()

    def get_st(self, _type=None, name=None):
        func = G_FUNC_LIST[_type]
        if not func:
            raise Exception("Type not found")
        with self.driver.session() as session:
            if name:
                result = session.execute_read(func,_type, name)
            else:
                result = session.execute_read(func,_type)
        self.driver.close()
        return result

    def del_st(self, _type=None, name=None):
        func = D_FUNC_LIST[_type]
        if not func:
            raise Exception("Type not found")
        with self.driver.session() as session:
            session.execute_write(func, _type, name)
        self.driver.close()
