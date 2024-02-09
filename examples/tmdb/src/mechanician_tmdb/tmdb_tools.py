import requests
from dotenv import load_dotenv
import os
from pprint import pprint
import json
from mechanician.ai_tools import AITools
import webbrowser
import logging

logger = logging.getLogger(__name__)

# https://developer.themoviedb.org

load_dotenv()

class TMDbHandler(AITools):
    """Class for interacting with the TMDb API."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {'Authorization': f'Bearer {self.api_key}'}
        self.config = self.get_tmdb_configuration()


    def get_tmdb_configuration(self):
        """Get the TMDb configuration."""
        url = f"{self.base_url}/configuration"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_poster_url(self, poster_path):
        """Get the full URL for a movie poster."""
        base_url = self.config["images"]["secure_base_url"]
        # poster_size = self.config["images"]["poster_sizes"][3]
        poster_size = 'original'
        return f"{base_url}{poster_size}{poster_path}"
    
    def get_poster_path(self, movie_id):
        """Get the poster path for a movie."""
        movie = self.get_movie_by_id({'id': movie_id})
        poster_path = movie.get('poster_path', None)
        return poster_path
    

    def display_movie_poster(self, params):
        """Open a movie poster in a web browser."""
        movie_id = params.get('movie_id', None)
        if movie_id is None:
            return "No movie_id found in request body"
        else:
            poster_path = self.get_poster_path(movie_id)
            url = self.get_poster_url(poster_path)
            webbrowser.open(url)
            return "Opened poster in web browser"
    

    def search_multi(self, query_params):
        """Search for a movie, a TV show, or a person."""
        query = query_params.get('query', None)
        url = f"{self.base_url}/search/multi"
        params = {
            "query": query
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    

    def search_movie(self, query_params):
        """Search for a movie by title and optionally by year."""
        query, year = query_params.get('query', None), query_params.get('year', None)
        url = f"{self.base_url}/search/movie"
        params = {
            "query": query
        }
        if year: params["year"] = year
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()


    def search_person(self, query_params):
        """Search for an actor by name."""
        query = query_params.get('query', None)
        url = f"{self.base_url}/search/person"
        params = {
            "query": query
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()
    

    def get_person_by_id(self, query_params):
        """Search for an actor by name."""
        id = query_params.get('id', None)
        url = f"{self.base_url}/person/{id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    

    def get_movie_by_id(self, query_params):
        """Get movie by ID."""
        id = query_params.get('id', None)
        url = f"{self.base_url}/movie/{id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    
    def get_actor_credits(self, query_params):
        """Returns a list of movies that a person been in."""
        person_id = query_params.get('person_id', None)
        url = f"{self.base_url}/person/{person_id}/movie_credits?language=en-US"
        response = requests.get(url, headers=self.headers)
        return response.json()


    def get_movie_credits(self, query_params):
        """Get cast credits for a movie based on the movie's ID."""
        movie_id = query_params.get('movie_id', None)
        url = f"{self.base_url}/movie/{movie_id}/credits?language=en-US"
        response = requests.get(url, headers=self.headers)
        return response.json()



def test():
    
    # Example usage
    api_key = os.getenv("TMDB_API_KEY")
    api_key = os.getenv("TMDB_READ_ACCESS_TOKEN")
    tmdb = TMDbHandler(api_key)

    # # Search for a movie
    # movie_title = "Inception"
    # movie_year = 2010
    # movie_search_results = tmdb.search_movie({'query': movie_title, 'year': movie_year})
    # pprint(movie_search_results)

    # print("\n\n\n##############################\n\n\n")
    # # Search for an actor
    # actor_name = "Leonardo DiCaprio"
    # actor_search_results = tmdb.search_person({'query': actor_name})
    # pprint(actor_search_results)

    # print("\n\n\n##############################\n\n\n")
    # print("PERSON BY ID")
    # # Search for an actor by id
    # actor_name = "Leonardo DiCaprio"
    # person_id = 6193
    # actor_search_results = tmdb.get_person_by_id({'id': person_id})
    # pprint(actor_search_results)


    # print("\n\n\n##############################\n\n\n")
    # print("TMDb CONFIGURATION")
    # config = tmdb.get_tmdb_configuration()
    # pprint(config)

    # print("\n\n\n##############################\n\n\n")
    # print("MOVIE BY ID")
    # # Search for an movie by id
    # movie_id = 27205
    # movie_result = tmdb.get_movie_by_id({'id': movie_id})
    # pprint(movie_result)


    # print("\n\n\n##############################\n\n\n")
    # print("VIEW POSTER")
    # tmdb.display_movie_poster({'movie_id': 27205})



    # print("\n\n\n##############################\n\n\n")
    # print("ACTOR CREDITS")
    # # Search for an movie by id
    # actor_name = "Leonardo DiCaprio"
    # person_id = 6193
    # actor_credits_result = tmdb.get_actor_credits({'person_id': person_id})
    # pprint(actor_credits_result)


    print("\n\n\n##############################\n\n\n")
    print("MOVIE CREDITS")
    # Search for an movie by id
    movie_id = 27205
    movie_credits_result = tmdb.get_movie_credits({'movie_id': movie_id})
    res = json.dumps(movie_credits_result, indent=4)
    with open('/tmp/movie_credits_result.json', 'w') as file:
        file.write(res)
    pprint(res)



# test()