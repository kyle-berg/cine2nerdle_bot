# import tmdb3 as tmdb
from telnetlib import EC
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import re
import pprint
import api_funcs as api

def start_game(driver):
    new_game_button = driver.find_element(By.CLASS_NAME, "battle-home-button")
    new_game_button.click()
    try:
        WebDriverWait(driver, timeout=60).until(lambda success: success.find_element(By.CLASS_NAME, "battle-choose-bans-button"))
    except:
        print("Exception occured with battle start")
        pass

    start_button = driver.find_element(By.CLASS_NAME, "battle-choose-bans-button")
    start_button.click()

def scan_site(driver):
    # print("scanning...")
    try:
        WebDriverWait(driver, timeout=1).until(lambda success: success.find_element(By.CLASS_NAME, "battle-board-game-over"))
    except:
        try:
            WebDriverWait(driver, timeout=1).until(lambda success: success.find_element(By.CLASS_NAME, "battle-input"))
        except:
            return 1
        else:
            return 0
    else:
        return 2

def play_movie(driver, played_movies):
    curr_movie = played_movies[0]
    print("Current movie: " + str(curr_movie["title"]) + " " + str(curr_movie["year"]))

    if len(played_movies) > 1:
        prev_movie = played_movies[1]
        print("Previous movie: " + str(prev_movie["title"]) + " " + str(prev_movie["year"]))
        links = api.gen_links(curr_movie, prev_movie)
    else:
        links = []

    movie = api.pick_movie(curr_movie=curr_movie, used_links=links, used_movies=played_movies)

    try:
        WebDriverWait(driver, timeout=2).until(lambda success: success.find_element(By.CLASS_NAME, "battle-input"))
    except:
        print("error finding the text box")
        pass
    else:
        text_box = driver.find_element(By.CLASS_NAME, "battle-input")
        if text_box.is_enabled():
            text_box.click()
            text_box.send_keys(str(movie[0]['title'] + " " + movie[0]['year']))
            text_box.send_keys(Keys.ENTER)

def main():
    service = webdriver.ChromeService(log_output='log.txt')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.cinenerdle2.app/battle")
    driver.implicitly_wait(3.0)

    start_game(driver)

    try:
        WebDriverWait(driver, timeout=32).until(lambda success: success.find_element(By.CLASS_NAME, "battle-board"))
    except:
        print("Exception occurred finding the battle board.")
        pass

    played_movies = []
    while True:
        game_status = scan_site(driver)
        if game_status == 0: # My turn
            print("Your turn!")
            time.sleep(1.0)
            try:
                WebDriverWait(driver, timeout=5).until(lambda success: success.find_elements(By.CLASS_NAME, "battle-movie"))
            except:
                print("Exception occurred finding the movies list.")
                pass
            else:
                movie_element_list = driver.find_elements(By.CLASS_NAME, "battle-movie")
                for movie in movie_element_list:
                    movie_str = movie.text
                    print(movie_str)
                    match = re.search(pattern=r"\d\n(.+?\))", string=movie_str, flags=re.MULTILINE)
                    if match:
                        movie_title = match.group(1)
                        match = re.search(r"(.+?)\((\d{4})\)", movie_title)
                        if not any(d['title'] == match.group(1).rstrip() for d in played_movies):
                            played_movies.append({'title': match.group(1).rstrip(), 'year': match.group(2)})
                    else:
                        print("No match found")
            print("Played movies: " + str(played_movies))
            play_movie(driver, played_movies)
        elif game_status == 1: # Their turn
            print("Their turn!")
        else:
            print("Game Over!")
        

if __name__ == "__main__":
    main()