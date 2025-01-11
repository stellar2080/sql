from neo4j import GraphDatabase

from src.graphdb.graphdb_base import GraphDB_Base


def create_node_tx(tx, node_type, name):
    cypher = f'''MERGE (a:{node_type} {{name:"{name}"}})'''
    tx.run(cypher)

def create_relation_tx(tx, relation_type, relation_name, type_a, name_a, type_b, name_b, priority):
    cypher = f'''
        MATCH (a:{type_a} {{name:"{name_a}"}}), (b:{type_b} {{name:"{name_b}"}}) 
        MERGE (a)-[:{relation_type} {{name:"{relation_name}",priority:{priority}}}]->(b)
    '''
    tx.run(cypher)

def create_index_tx(tx, index_name, node_type):
    cypher = f'''CREATE INDEX {index_name} FOR (a:{node_type}) ON (a.name)'''
    tx.run(cypher)

def get_nodes_tx(tx, node_type=None, name=None):
    if node_type == "Node":
        if name:
            cypher = f'''MATCH (a) WHERE a.name="{name}" RETURN a'''
        else:
            cypher = '''MATCH (a) RETURN a'''
    else:
        if name:
            cypher = f'''MATCH (a:{node_type}) WHERE a.name="{name}" RETURN a'''
        else:
            cypher = f'''MATCH (a:{node_type}) RETURN a'''

    result = tx.run(cypher)
    for record in result:
        node = record['a']
        print("[Node]")
        print("Labels:", list(node.labels) , "\nName:", node['name'])
        print("-"*20)

    return result

def get_relation_tx(tx, relation_type=None,relation_name=None):
    if relation_type == "Fig":
        if relation_name:
            cypher = f'''MATCH (a)-[r]->(b) WHERE r.name="{relation_name}" RETURN a, r, b'''
        else:
            cypher = f'''MATCH (a)-[r]->(b) RETURN a, r, b'''
    else:
        if relation_name:
            cypher = f'''MATCH (a)-[r:{relation_type}]->(b) WHERE r.name="{relation_name}" RETURN a, r, b'''
        else:
            cypher = f'''MATCH (a)-[r:{relation_type}]->(b) RETURN a, r, b'''

    result = tx.run(cypher)
    for record in result:
        a = record['a']
        b = record['b']
        r = record['r']
        print("[Relation]")
        print(a['name'], "-[:", r.type, f" {{name={r.name}}}]->", b['name'])
        print("-" * 20)

    return result

def show_index_tx(tx):
    cypher = "SHOW INDEXES"
    result = tx.run(cypher)
    for record in result:
        print("[Index]")
        print(record)
        print("-" * 20)

    return result


def del_nodes_tx(tx, node_type=None, name=None):
    if node_type == "Node":
        if name:
            cypher = f'''MATCH (a) WHERE a.name = "{name}“ DETACH DELETE a'''
        else:
            cypher = '''MATCH (a) DETACH DELETE a'''
    else:
        if name:
            cypher = f'''MATCH (a:{node_type}) WHERE a.name = ”{name}" DETACH DELETE a'''
        else:
            cypher = f'''MATCH (a:{node_type}) DETACH DELETE a'''

    tx.run(cypher)

def del_relation_tx(tx, relation_type=None, relation_name=None):
    if relation_type == "Relation":
        if relation_name:
            cypher = f'''MATCH (a)-[r]->(b) WHERE r.name="{relation_name}" DELETE r'''
        else:
            cypher = f'''MATCH (a)-[r]->(b) DELETE r'''
    else:
        if relation_name:
            cypher = f'''MATCH (a)-[r:{relation_type}]->(b) WHERE r.name="{relation_name}" DELETE r'''
        else:
            cypher = f'''MATCH (a)-[r:{relation_type}]->(b) DELETE r'''

    tx.run(cypher)

def del_index_tx(tx, index_name):
    if not index_name:
        raise Exception("Please specify the index name")
    cypher = f"DROP INDEX {index_name}"

    tx.run(cypher)

FIG_LIST = ["EQ","Add","Mnd","Sub","Mul","Dvd","Dvs"]

C_FUNC_LIST = {
    "Elem": create_node_tx,
    "Mid": create_node_tx,
    "Col": create_node_tx,

    "Op": create_relation_tx,
}

G_FUNC_LIST = {
    "Elem": get_nodes_tx,
    "Mid": get_nodes_tx,
    "Col": get_nodes_tx,
    "Node": get_nodes_tx,

    "Op": create_relation_tx,
    "Relation": get_relation_tx,
}

D_FUNC_LIST = {
    "Elem": del_nodes_tx,
    "Mid": del_nodes_tx,
    "Col": del_nodes_tx,
    "Node": del_nodes_tx,

    "Op": del_relation_tx,
    "Relation": del_relation_tx,
}

op_map = {
    "Add": " + ",
    "Sub": " - ",
    "Mul": " * ",
    "Dvs": " / ",
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
        print(f"Node: (:{node_type}, {{name:{name}}}) merged.")

    def create_relation(self, relation_type, relation_name, node_type_a, name_a, node_type_b, name_b, priority):
        func = C_FUNC_LIST[relation_type]
        if not func:
            raise Exception("Relation_type not supported")
        if relation_name not in FIG_LIST:
            raise Exception("Relation_name not supported")
        with self.driver.session() as session:
            session.execute_write(func, relation_type, relation_name, node_type_a, name_a, node_type_b, name_b, priority)
        self.driver.close()
        print(f"Relation: ({name_a})-[:{relation_type}{{name:{relation_name}}}]->({name_b}) merged.")

    def create_by_list(self, _list):
        with self.driver.session() as session:
            for item in _list:
                if len(item) == 2:
                    node_type, name = item
                    func = C_FUNC_LIST[node_type]
                    if not func:
                        raise Exception("Node_type not found")
                    session.execute_write(func, node_type, name)
                    print(f'''Node: (:{node_type} {{name:"{name}"}}) merged.''')
                else:
                    priority = 0
                    if len(item) == 6:
                        relation_type, relation_name, node_type_a, name_a, node_type_b, name_b = item
                    elif len(item) == 7:
                        relation_type, relation_name, node_type_a, name_a, node_type_b, name_b, priority = item
                    func = C_FUNC_LIST[relation_type]
                    if not func:
                        raise Exception("Relation_type not supported")
                    if relation_name not in FIG_LIST:
                        raise Exception("Relation_name not supported")
                    session.execute_write(func, relation_type, relation_name, node_type_a, name_a, node_type_b, name_b, priority)
                    print(f'''Relation: ({name_a})-[:{relation_type} {{name:"{relation_name}"}}]->({name_b}) merged.''')
        self.driver.close()


    def get_sth(self, _type, _name=None):
        func = G_FUNC_LIST[_type]
        if not func:
            raise Exception("Type not found")
        with self.driver.session() as session:
                result = session.execute_read(func,_type, _name)
        self.driver.close()
        return result

    def del_sth(self, _type, _name=None):
        func = D_FUNC_LIST[_type]
        if not func:
            raise Exception("Type not found")
        with self.driver.session() as session:
            session.execute_write(func, _type, _name)
        self.driver.close()
        print("Successfully delete.")

    def del_all(self):
        with self.driver.session() as session:
            session.execute_write(del_nodes_tx,"Node")
            session.execute_write(del_relation_tx,"Relation")
        self.driver.close()
        print("Successfully delete.")

    def create_index(self, index_name, node_type):
        with self.driver.session() as session:
            session.execute_write(create_index_tx, index_name, node_type)
        self.driver.close()
        print(f"Index: {index_name} (:{node_type}) created.")

    def del_index(self, index_name):
        with self.driver.session() as session:
            session.execute_write(del_index_tx, index_name)
        self.driver.close()
        print(f"Index: {index_name} deleted.")

    def show_index(self):
        with self.driver.session() as session:
            session.execute_write(show_index_tx)
        self.driver.close()

    def recursion(self, node_type, _name, session):
        return_str = ""
        cypher = f"""
            MATCH path = (root:{node_type} {{name:"{_name}"}})-[rel:Op]->(child)
            ORDER BY rel.priority ASC
            RETURN rel, child
        """
        result = session.run(cypher)
        for record in result:
            rel_name = record['rel']['name']
            (child_type,) = record['child'].labels
            child_name = record['child']['name']
            if child_type != "Col":
                append_str = '(' + self.recursion(child_type, child_name, session) + ')'
            else:
                append_str = child_name
            if len(return_str) != 0:
                return_str += op_map[rel_name]
            return_str += append_str

        return return_str

    def query(self, node_type, name):
        with self.driver.session() as session:
            result = self.recursion(node_type, name, session)
            string = name + " = " + result
            print(string)
        self.driver.close()