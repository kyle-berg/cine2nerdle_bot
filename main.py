# import tmdb3 as tmdb
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
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
    print("Scanning...")
    try:
        WebDriverWait(driver, timeout=3).until(lambda success: success.find_element(By.CLASS_NAME, "battle-input"))
    except:
        # print("Exception determining if it's our turn")
        pass
    else:
        if driver.find_element(By.CLASS_NAME, "battle-input").is_displayed():
            return 0
        
    try:
        WebDriverWait(driver, timeout=3).until(lambda success: success.find_element(By.CLASS_NAME, "opponents-turn"))
    except:
        # print("Exception determining if it's their turn")
        pass
    else:
        if driver.find_element(By.CLASS_NAME, "opponents-turn").is_displayed():
            return 1
        
    

def update_movies(driver, played_movies):
    print("Updating movies...")
    try:
        WebDriverWait(driver, timeout=5).until(lambda success: success.find_elements(By.CLASS_NAME, "battle-movie"))
    except:
        print("Exception occurred finding the movies list.")
        pass
    else:
        movie_element_list = driver.find_elements(By.CLASS_NAME, "battle-movie")
        for movie in movie_element_list:
            movie_str = movie.text
            # print(movie_str)
            matches = re.findall(pattern=r"\d\n(.+?\))", string=movie_str, flags=re.MULTILINE)
            for match in matches:
                # movie_title = match.group(1)
                match2 = re.search(r"(.+?)\((\d{4})\)", match)
                if not any(d['title'] == match2.group(1).rstrip() for d in played_movies):
                    movie = {'title': match2.group(1).rstrip(), 'year': match2.group(2)}
                    print(len(played_movies))
                    played_movies.insert(len(played_movies), movie)

def play_movie(driver, played_movies):
    print("Played movies: " + str(played_movies))
    curr_movie = played_movies[-1]
    print("Current movie: " + str(curr_movie["title"]) + " " + str(curr_movie["year"]))

    if len(played_movies) > 1:
        prev_movie = played_movies[-2]
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
            # text_box.send_keys(Keys.ENTER)
            try:
                WebDriverWait(driver, timeout=3).until(lambda success: success.find_element(By.CLASS_NAME, "battle-suggestion"))
            except:
                print("error finding the movie")
                pass
            else:
                selection = driver.find_element(By.CLASS_NAME, "battle-suggestion")
                selection.click()
            

def main():
    service = webdriver.ChromeService(log_output='log.txt')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_extension('CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_58_0_0.crx')

    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.cinenerdle2.app/battle")
    time.sleep(3.0)

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
            time.sleep(2.0)
            update_movies(driver, played_movies)
            play_movie(driver, played_movies)
            WebDriverWait(driver, timeout=3).until(lambda success: success.find_element(By.CLASS_NAME, "opponents-turn"))
        elif game_status == 1: # Their turn
            print("Their turn!")
            update_movies(driver, played_movies)
        else:
            print("Game Over!")
            break
        

if __name__ == "__main__":
    main()