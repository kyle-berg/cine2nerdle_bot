import tmdbsimple as tmdb
import pprint

tmdb.API_KEY = 'fe50c0b66d13f4e597422d3bec8c398b'


def get_movie_info(movie_name, year=None):
    search = tmdb.Search()
    response = search.movie(query=movie_name, year=year)

    if not response['results']:
        return "No movie found with the given name and year."

    # Get the first movie in the results
    movie = response['results'][0]

    # Return a dictionary with the title and year
    return {'title': movie['title'], 'year': movie['release_date'][:4]}


def get_movies(actor_name):
    """
    Gets movies of an actor
    :param actor_name:
    :return:
    """

    search = tmdb.Search()
    actor_search = search.person(query=actor_name)

    if not actor_search['results']:
        return f"No results found for actor named {actor_name}"

    actor_id = actor_search['results'][0]['id']
    person = tmdb.People(actor_id)
    movie_credits = person.movie_credits()

    movies = [{'title': movie['title'], 'year': movie['release_date'][:4]} for movie in movie_credits['cast']]

    return movies


def get_cast(movie_name, release_year=None):
    """
    Gets cast of a movie
    :param movie_name:
    :param release_year:
    :return:
    """

    search = tmdb.Search()
    movie_search = search.movie(query=movie_name)

    if not movie_search['results']:
        return f"No results found for movie named {movie_name}"

    if release_year:
        movies = [movie for movie in movie_search['results'] if str(release_year) in movie['release_date']]
    else:
        movies = movie_search['results']

    if not movies:
        return f"No results found for movie named {movie_name} released in {release_year}"

    movie_id = movies[0]['id']
    movie = tmdb.Movies(movie_id)

    movie_credits = movie.credits()
    cast = movie_credits['cast']

    cast_list = [member['name'] for member in cast]

    return cast_list


def pick_movie(curr_movie, used_links, used_movies):
    cast = get_cast(curr_movie['title'], curr_movie['year'])

    connection = cast[0]
    for actor in cast:
        if actor not in used_links:
            connection = actor  # could be saved as a list of valid actors
            break

    movies = get_movies(connection)
    for movie in movies:
        if movie not in used_movies:
            print("Recommended play: " + str(movie))
            return [movie, connection]


def gen_links(movie1, movie2):
    cast1 = get_cast(movie1['title'], movie1['year'])
    cast2 = get_cast(movie2['title'], movie2['year'])
    cast3 = []
    for actor in cast1:
        if actor in cast2:
            cast3.append(actor)
    return cast3


def game():
    used_movies = []
    used_links = []
    bot_movie = None
    winning = True;

    while winning:

        movie = get_movie_info(input('Enter a movie: '),input('Enter a year (optional): '))

        if movie in used_movies:
            print('Movie already used')
            return
        elif bot_movie and not gen_links(movie, bot_movie):
            print('No links between movies: "' + movie['title'] + '" and "' + bot_movie['title'] + '"')
            return
        else:
            used_movies.append(movie)
            if bot_movie:
                for link in gen_links(movie, bot_movie): used_links.append(link)
                print('Links:', gen_links(movie, bot_movie))
            print()

        bot_movie = pick_movie(movie, used_links, used_movies)
        print('I choose "' + bot_movie[0]['title'] + '" via ' + bot_movie[1])
        bot_movie = bot_movie[0]
        used_movies.append(bot_movie)
        for link in gen_links(movie, bot_movie): used_links.append(link)


if __name__ == '__main__':
    game()
