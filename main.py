# import tmdb3 as tmdb
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

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
    try:
        WebDriverWait(driver, timeout=5).until(lambda success: success.find_element(By.CLASS_NAME, "battle-board-movie-number"))
    except:
        print("Exception occurred finding the movie number.")
        return True
    
    movie_number = driver.find_element(By.CLASS_NAME, "battle-board-movie-number").text
    movie_number -= 1
    class_name = "battle-board-movie-" + movie_number

    movie_title = driver.find_element(By.CLASS_NAME, class_name).text
    print(movie_title)

    try:
        WebDriverWait(driver, timeout=2).until(lambda success: success.find_element(By.CLASS_NAME, "battle-board-game-over"))
    except:
        try:
            WebDriverWait(driver, timeout=2).until(lambda success: success.find_element(By.CLASS_NAME, "opponents-turn"))
        except:
            print("Your turn!")
            text_box = driver.find_element(By.CLASS_NAME, "battle-board-input")
            play_movie(text_box=text_box, movie_title=movie_title)
            return False
        else:
            print("Not your turn!")
            return False
    else:
        print("Game Over!")
        return True

def play_movie(text_box, movie_title):
    print("played movie")

def main():
    service = webdriver.ChromeService(log_output='log.txt')

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=service, options=options)

    driver.get("https://www.cinenerdle2.app/battle")
    driver.implicitly_wait(3.0)

    start_game(driver)
    
    while not scan_site(driver):
        driver.implicitly_wait(1.0)
        pass

if __name__ == "__main__":
    main()