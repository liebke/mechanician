from arango import ArangoClient
import os
from dotenv import load_dotenv
from pprint import pprint

from mechanician_tmdb.tmdb_tools import TMDbHandler
from mechanician_tmdb.tmdb_tool_schemas import tool_schemas

import json

# https://github.com/ArangoDB-Community/python-arango
# https://docs.python-arango.com/en/main/

load_dotenv()

# def rename_key(dict, old_key, new_key):
#     dict[new_key] = str(dict.pop(old_key))
#     return dict

# Initialize the ArangoDB client
client = ArangoClient(hosts='http://localhost:8529')
tmdb = TMDbHandler(os.getenv("TMDB_READ_ACCESS_TOKEN"))

# Connect to the database with the root user
# Replace 'yourpassword' with the password you set for the ArangoDB Docker instance
db = client.db('_system', username='root', password=os.getenv("ARANGO_ROOT_PASSWORD"))

# Create a new database for our movie data
if not db.has_database('movie_database'):
    db.create_database('movie_database')

# Delete the collection.
# db.delete_collection('movies')
# db.delete_collection('people')
# db.delete_collection('credits')
# db.delete_collection('credits_of')

def create_edge_collection(collection_name):
    if not db.has_collection(collection_name):
        edge_collection = db.create_collection(collection_name, edge=True)
        print(f"Edge collection '{collection_name}' created.")
    else:
        edge_collection = db.collection(collection_name)
        print(f"Edge collection '{collection_name}' already exists.")
    return edge_collection

# Create collections for movies, cast, and crew if they do not exist
if not db.has_collection('movies'):
    db.create_collection('movies')


if not db.has_collection('people'):
    db.create_collection('people')

if not db.has_collection('credits'):
    db.create_collection('credits')

create_edge_collection('credits_of')


# if not db.has_collection('crew'):
#     db.create_collection('crew')

# Function to insert movie data
# def insert_movie(title, year, genre):
#     movies = db.collection('movies')
#     movies.insert({'title': title, 'year': year, 'genre': genre})
    
def insert_movie(movie_id):
    movies = db.collection('movies')
    movie = tmdb.get_movie_by_id({'id': movie_id})
    movie['_key'] = str(movie['id'])  # Create _key from integer ID
    pprint(movie)
    if movies.has(movie['_key']):
        return movies.update(movie)
    else:
        return movies.insert(movie)



def edge_exists(edge_collection, from_vertex, to_vertex):
    cursor = edge_collection.find({'_from': from_vertex, '_to': to_vertex}, limit=1)
    return cursor.count() > 0

def insert_credit(credits, credit):
    credit['_key'] = str(credit['id'])  # Create _key from integer ID
    if credits.has(credit['_key']):
        return credits.update(credit)
    else:
        return credits.insert(credit)

def insert_credits(movie_id):
    # movie_graph = create_graph('movie_graph', edge_definitions)
    credits_of = db.collection('credits_of')
    credits = db.collection('credits')
    movie_credits = tmdb.get_movie_credits({'movie_id': movie_id})
    if movie_credits.get('success') is False:
        print("Movie credits not found")
        return
    ###
    res = json.dumps(movie_credits, indent=4)
    with open('/tmp/movie_credits_result.json', 'w') as file:
        file.write(res)
    ###
    movie_key = str(movie_credits.get('id'))
    print(f"Cast size: {len(movie_credits['cast'])}")
    results = []
    for credit in movie_credits['cast']:
        insert_credit(credits, credit)
        credit_of = {}
        credit_of['_from'] = f"credits/{str(credit['id'])}"
        credit_of['_to'] = f"movies/{movie_key}"
        if not edge_exists(credits_of, credit_of['_from'], credit_of['_to']):
            print(f"Credit from {credit['name']} to {movie_key} does not exist, inserting...")
            results.append(credits_of.insert(credit_of))
        else:
            print(f"Credit from {movie_key} to {credit['name']} already exists, ignoring...")
    
    return results


# Function to insert cast data
def insert_person(person_id):
    people = db.collection('people')
    person = tmdb.get_person_by_id({'id': person_id})
    pprint(person)
    person['_key'] = str(person['id'])  # Create _key from integer ID
    if people.has(person['_key']):
        return people.update(person)
    else:
        return people.insert_replace(person)

# Function to get a movie by id
def get_movie(movie_id):
    movies = db.collection('movies')
    movie = movies.get(str(movie_id))
    return movie


# Function to search for movies
def search_movies(search_term):
    aql = "FOR m IN movies FILTER LIKE(m.title, @title, true) RETURN m"
    cursor = db.aql.execute(aql, bind_vars={'title': '%' + search_term + '%'})
    return [doc for doc in cursor]


def search_people(search_term):
    aql = "FOR p IN people FILTER LIKE(p.name, @name, true) RETURN p"
    cursor = db.aql.execute(aql, bind_vars={'name': '%' + search_term + '%'})
    return [doc for doc in cursor]

def get_person_by_id(person_id):
    people = db.collection('people')
    person = people.get(str(person_id))
    return person

def get_credit_by_id(credit_id):
    credits = db.collection('credits')
    credit = credits.get(str(credit_id))
    return credit

def get_movie_credit_edges(movie_id):
    credits_of = db.collection('credits_of')
    movie_credits = credits_of.find({'_to': f"movies/{str(movie_id)}"})
    return [doc for doc in movie_credits]


def get_people_in_movie(movie_id):
    # Define the AQL query
    query = """
    FOR v IN 1..1 INBOUND @start_vertex credits_of
        FILTER IS_SAME_COLLECTION('credits', v)
        RETURN {'_id': v._id, 'name': v.name}
    """

    print(query)
    # Execute the AQL query
    # cursor = db.aql.execute(query, bind_vars={'start_vertex': f'movies/{movie_id}'})
    cursor = db.aql.execute(query, bind_vars={'start_vertex': movie_id})
    # cursor = db.aql.execute(query)

    # Return the result as a list
    return list(cursor)

# Example usage
# insert_movie('Inception', 2010, 'Sci-Fi')
# insert_cast('Inception', 'Leonardo DiCaprio')

# print("\n\n\n##############################\n\n\n")
# print("INSERT MOVIE")
# pprint(insert_movie(27205))

# print("\n\n\n##############################\n\n\n")
# print("INSERT PERSON")
# pprint(insert_person(6193))

# print("\n\n\n##############################\n\n\n")
# print("INSERT CREDITS")
# pprint(insert_credits(27205))

# Search for a movie
# print("\n\n\n##############################\n\n\n")
# print("SEARCH MOVIES")
# movies = search_movies('Inception')
# pprint(movies)

# print("\n\n\n##############################\n\n\n")
# print ("GET MOVIE")
# movie = get_movie(27205)
# pprint(movie)


print("\n\n\n##############################\n\n\n")
print ("GET MOVIE CREDITS")
movie_credits = get_movie_credit_edges(27205)
pprint(movie_credits)


print("\n\n\n##############################\n\n\n")
print ("GET MOVIE CREDIT")
movie_credit = get_credit_by_id("credits/6193")
pprint(movie_credit)



print("\n\n\n##############################\n\n\n")
print ("GET PEOPLE IN MOVIE")
people_in_movie = get_people_in_movie("movies/27205")
pprint(people_in_movie)


# print("\n\n\n##############################\n\n\n")
# print("SEARCH PEOPLE")
# people = search_people('Leonardo DiCaprio')
# pprint(people)  


