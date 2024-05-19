import requests
import os
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def create_browser():
    # Creates a selenium browser and opens the Facebook page
    browser = webdriver.Chrome()
    browser.get("https://www.facebook.com/groups/900072927547214/media/photos")
    return browser


def save_post_ID(browser, existing_csv_file):

    # ---------------------------------------------------------------------- #
    # Save post ID inside CSV file
    # ---------------------------------------------------------------------- #

    try:
        container_xpath = "//div[@class='x78zum5 x1q0g3np x1a02dak']"
        container = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, container_xpath))
        )
        a_elements = container.find_elements(By.XPATH, ".//a[contains(@class, 'x1i10hfl')]")

        with open(existing_csv_file, mode='a', newline='', encoding='latin-1') as csv_file:
            fieldnames = ['post_link', 'name', 'classification', 'status']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            for i, a_element in enumerate(a_elements):
                post_link = a_element.get_attribute("href")

                if not post_link_exists(existing_csv_file, post_link):
                    writer.writerow({'post_link': post_link, 'name': '', 'classification': '', 'status': 'Empty'})
                    print(f"Post Link {post_link} added to existing CSV file")

        print(f"Number of images found: {len(a_elements)}")

    except Exception as e:
        print("No images found or an error occurred:", e)



def post_link_exists(existing_csv_file, post_link):

    # ---------------------------------------------------------------------- #
    # Check if post ID already exists
    # ---------------------------------------------------------------------- #
    
    with open(existing_csv_file, mode='r', encoding='latin-1') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['post_link'] == post_link:
                print(f"Post Link {post_link} already exists in the CSV file")
                return True
    return False

home = os.path.expanduser("~")
existing_csv_file = "temp_post_ID.csv"
browser = create_browser()
input("Press Enter to collect images...")

save_post_ID(browser, existing_csv_file)
browser.quit()
