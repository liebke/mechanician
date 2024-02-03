from arango import ArangoClient
import os
from dotenv import load_dotenv
from pprint import pprint

# https://github.com/ArangoDB-Community/python-arango

load_dotenv()

# Initialize the ArangoDB client
client = ArangoClient(hosts='http://localhost:8529')
db = client.db('_system', username='root', password=os.getenv("ARANGO_ROOT_PASSWORD"))

# Create a new database for our movie data
if not db.has_database('game_of_thrones_database'):
    db.create_database('game_of_thrones_database')


# Create collections for movies, cast, and crew if they do not exist
if not db.has_collection('characters'):
    db.create_collection('characters')

    
insert_query = """
LET data = [
    { "name": "Ned", "surname": "Stark", "alive": true, "age": 41, "traits": ["A","H","C","N","P"] },
    { "name": "Robert", "surname": "Baratheon", "alive": false, "traits": ["A","H","C"] },
    { "name": "Jaime", "surname": "Lannister", "alive": true, "age": 36, "traits": ["A","F","B"] },
    { "name": "Catelyn", "surname": "Stark", "alive": false, "age": 40, "traits": ["D","H","C"] },
    { "name": "Cersei", "surname": "Lannister", "alive": true, "age": 36, "traits": ["H","E","F"] },
    { "name": "Daenerys", "surname": "Targaryen", "alive": true, "age": 16, "traits": ["D","H","C"] },
    { "name": "Jorah", "surname": "Mormont", "alive": false, "traits": ["A","B","C","F"] },
    { "name": "Petyr", "surname": "Baelish", "alive": false, "traits": ["E","G","F"] },
    { "name": "Viserys", "surname": "Targaryen", "alive": false, "traits": ["O","L","N"] },
    { "name": "Jon", "surname": "Snow", "alive": true, "age": 16, "traits": ["A","B","C","F"] },
    { "name": "Sansa", "surname": "Stark", "alive": true, "age": 13, "traits": ["D","I","J"] },
    { "name": "Arya", "surname": "Stark", "alive": true, "age": 11, "traits": ["C","K","L"] },
    { "name": "Robb", "surname": "Stark", "alive": false, "traits": ["A","B","C","K"] },
    { "name": "Theon", "surname": "Greyjoy", "alive": true, "age": 16, "traits": ["E","R","K"] },
    { "name": "Bran", "surname": "Stark", "alive": true, "age": 10, "traits": ["L","J"] },
    { "name": "Joffrey", "surname": "Baratheon", "alive": false, "age": 19, "traits": ["I","L","O"] },
    { "name": "Sandor", "surname": "Clegane", "alive": true, "traits": ["A","P","K","F"] },
    { "name": "Tyrion", "surname": "Lannister", "alive": true, "age": 32, "traits": ["F","K","M","N"] },
    { "name": "Khal", "surname": "Drogo", "alive": false, "traits": ["A","C","O","P"] },
    { "name": "Tywin", "surname": "Lannister", "alive": false, "traits": ["O","M","H","F"] },
    { "name": "Davos", "surname": "Seaworth", "alive": true, "age": 49, "traits": ["C","K","P","F"] },
    { "name": "Samwell", "surname": "Tarly", "alive": true, "age": 17, "traits": ["C","L","I"] },
    { "name": "Stannis", "surname": "Baratheon", "alive": false, "traits": ["H","O","P","M"] },
    { "name": "Melisandre", "alive": true, "traits": ["G","E","H"] },
    { "name": "Margaery", "surname": "Tyrell", "alive": false, "traits": ["M","D","B"] },
    { "name": "Jeor", "surname": "Mormont", "alive": false, "traits": ["C","H","M","P"] },
    { "name": "Bronn", "alive": true, "traits": ["K","E","C"] },
    { "name": "Varys", "alive": true, "traits": ["M","F","N","E"] },
    { "name": "Shae", "alive": false, "traits": ["M","D","G"] },
    { "name": "Talisa", "surname": "Maegyr", "alive": false, "traits": ["D","C","B"] },
    { "name": "Gendry", "alive": false, "traits": ["K","C","A"] },
    { "name": "Ygritte", "alive": false, "traits": ["A","P","K"] },
    { "name": "Tormund", "surname": "Giantsbane", "alive": true, "traits": ["C","P","A","I"] },
    { "name": "Gilly", "alive": true, "traits": ["L","J"] },
    { "name": "Brienne", "surname": "Tarth", "alive": true, "age": 32, "traits": ["P","C","A","K"] },
    { "name": "Ramsay", "surname": "Bolton", "alive": true, "traits": ["E","O","G","A"] },
    { "name": "Ellaria", "surname": "Sand", "alive": true, "traits": ["P","O","A","E"] },
    { "name": "Daario", "surname": "Naharis", "alive": true, "traits": ["K","P","A"] },
    { "name": "Missandei", "alive": true, "traits": ["D","L","C","M"] },
    { "name": "Tommen", "surname": "Baratheon", "alive": true, "traits": ["I","L","B"] },
    { "name": "Jaqen", "surname": "H'ghar", "alive": true, "traits": ["H","F","K"] },
    { "name": "Roose", "surname": "Bolton", "alive": true, "traits": ["H","E","F","A"] },
    { "name": "The High Sparrow", "alive": true, "traits": ["H","M","F","O"] }
]

FOR d IN data
    INSERT d INTO characters
"""

aql = db.aql
# python-arango
# aql.execute(insert_query)

all_characters_names = """
FOR c IN characters
    RETURN c.name
"""

query_result = aql.execute(all_characters_names)
for doc in  query_result:
    print(doc)
    print()

# Creating collections with python-arango
# Since the collection is created above this should always pass
if db.has_collection("child_of"):
  pass
else:
  db.create_collection("child_of", edge=True)

create_edges_query = """
LET data = [
    {
        "parent": { "name": "Ned", "surname": "Stark" },
        "child": { "name": "Robb", "surname": "Stark" }
    }, {
        "parent": { "name": "Ned", "surname": "Stark" },
        "child": { "name": "Sansa", "surname": "Stark" }
    }, {
        "parent": { "name": "Ned", "surname": "Stark" },
        "child": { "name": "Arya", "surname": "Stark" }
    }, {
        "parent": { "name": "Ned", "surname": "Stark" },
        "child": { "name": "Bran", "surname": "Stark" }
    }, {
        "parent": { "name": "Catelyn", "surname": "Stark" },
        "child": { "name": "Robb", "surname": "Stark" }
    }, {
        "parent": { "name": "Catelyn", "surname": "Stark" },
        "child": { "name": "Sansa", "surname": "Stark" }
    }, {
        "parent": { "name": "Catelyn", "surname": "Stark" },
        "child": { "name": "Arya", "surname": "Stark" }
    }, {
        "parent": { "name": "Catelyn", "surname": "Stark" },
        "child": { "name": "Bran", "surname": "Stark" }
    }, {
        "parent": { "name": "Ned", "surname": "Stark" },
        "child": { "name": "Jon", "surname": "Snow" }
    }, {
        "parent": { "name": "Tywin", "surname": "Lannister" },
        "child": { "name": "Jaime", "surname": "Lannister" }
    }, {
        "parent": { "name": "Tywin", "surname": "Lannister" },
        "child": { "name": "Cersei", "surname": "Lannister" }
    }, {
        "parent": { "name": "Tywin", "surname": "Lannister" },
        "child": { "name": "Tyrion", "surname": "Lannister" }
    }, {
        "parent": { "name": "Cersei", "surname": "Lannister" },
        "child": { "name": "Joffrey", "surname": "Baratheon" }
    }, {
        "parent": { "name": "Jaime", "surname": "Lannister" },
        "child": { "name": "Joffrey", "surname": "Baratheon" }
    }
]

FOR rel in data
    LET parent_id = FIRST(
        FOR c IN characters
            FILTER c.name == rel.parent.name
            FILTER c.surname == rel.parent.surname
            LIMIT 1
            RETURN c._id
    )
    LET child_id = FIRST(
        FOR c IN characters
            FILTER c.name == rel.child.name
            FILTER c.surname == rel.child.surname
            LIMIT 1
            RETURN c._id
    )
    FILTER parent_id != null AND child_id != null
    INSERT { _from: child_id, _to: parent_id } INTO child_of
    RETURN NEW
"""
# python-arango
# query_result = aql.execute(create_edges_query)


sansa_parents_query = """
// First find the start node, i.e., sansa
FOR c IN characters
    FILTER c.name == "Sansa"
    // Then start a Graph traversal from that start node
    FOR v IN 1..1 OUTBOUND c child_of
    RETURN DISTINCT v.name
"""
# python-arango
query_result = aql.execute(sansa_parents_query)
print("######################")
print("Sansa's parents:")
for doc in  query_result:
    print(doc)
    print()



ned_children_query = """
// First find the start node, i.e., ned
FOR c IN characters
    FILTER c.name == "Ned"
    // Then start a Graph traversal from that start node
    FOR v IN 1..1 INBOUND c child_of
    RETURN DISTINCT v.name
"""
# python-arango
query_result = aql.execute(ned_children_query)

print("######################")
print("Ned's children:")
for doc in  query_result:
    print(doc)
    print()

tywin_grandchildren_query = """
// First find the start node, i.e., ned
FOR c IN characters
    FILTER c.name == "Tywin"
    // Then start a Graph traversal from that start node
    FOR v IN 2..2 INBOUND c child_of
    RETURN DISTINCT v.name
"""
# python-arango
query_result = aql.execute(tywin_grandchildren_query)

print("######################")
print("Tywin's children:")

for doc in  query_result:
    print(doc)
    print()


joffrey_ancestors_query = """
FOR c IN characters
    FILTER c.name == "Joffrey"
    FOR v IN 1..2 OUTBOUND c child_of
        RETURN DISTINCT v.name
"""
# python-arango
query_result = aql.execute(joffrey_ancestors_query)

print("######################")
print("Joffrey's Ancestors:")
for doc in  query_result:
    print(doc)
    print()