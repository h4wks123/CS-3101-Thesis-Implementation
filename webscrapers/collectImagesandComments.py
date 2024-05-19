import requests
import os
import re
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options


def store_into_stack(start_row, end_row):
    csv_file_path = "C:\\Users\\ivanne bayer\\Desktop\\Computer Science\\Comp Sci - Yr. 3 second sem\\CS 3201 - Thesis 1\\CS 3201 - Web Scraper BAYER\\temp_post_ID.csv"
    first_column_values = []

    with open(csv_file_path, 'r') as file:
        csv_reader = csv.reader(file)
        
        for _ in range(start_row - 1):
            next(csv_reader)
        
        for row_number, row in enumerate(csv_reader, start=start_row):
            if row_number > end_row:
                break
            
            first_column_value = row[0]
            first_column_values.append(first_column_value)

    return first_column_values



def iterate_the_links(first_column_values):
    zoom_level = 0.6

    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument(f"--force-device-scale-factor={zoom_level}")
    
    # Initialize Chrome WebDriver with options
    browser = webdriver.Chrome(options=chrome_options)
    
    try:
        while first_column_values:
            link = first_column_values.pop(0)
            print("Opening link:", link)
            
            modified_link = re.sub(r'&set=g.*', '', link)
            
            browser.get(modified_link)
            close_login_modal(browser)
            save_to_svg(browser, link) 

            browser.close()
            
            if first_column_values:
                browser = webdriver.Chrome(options=chrome_options)
    finally:
        browser.quit()



def close_login_modal(browser):
    try:
        # Wait for the close button to be clickable
        close_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close']"))
        )
        # Click the close button to close the modal
        close_button.click()
    except TimeoutException:
        # If the modal is not found within the timeout period, continue without closing
        print("Login modal not found within timeout period.")
    except Exception as e:
        # Handle any other exceptions
        print("An error occurred while closing the login modal:", e)



def save_to_svg(browser, link):
    try:
        post_container = browser.find_element(By.CLASS_NAME, "x9f619")
        image_element = post_container.find_element(By.TAG_NAME, "img")
        image_src = image_element.get_attribute("src")
        print("Image Source:", image_src)
        
        comments_container = browser.find_element(By.XPATH, "//div[@class='x1pi30zi x1swvt13']")
        
        # Initially locate the comments
        comments = comments_container.find_elements(By.XPATH, ".//div[@dir='auto']")
        
        first_row = None
        comment_text = None

        if comments:
            see_more_button = None
            
            try:
                see_more_button = browser.find_element(By.XPATH, "//div[@class='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f' and @role='button' and text()='See more']")
            except NoSuchElementException:
                pass

            if see_more_button:
                # Click the "See more" button
                see_more_button.click()
                print("Clicked See more button")
                
                comments_container = browser.find_element(By.XPATH, "//div[@class='x1pi30zi x1swvt13']")
                comments = comments_container.find_elements(By.XPATH, ".//div[@dir='auto']")

        for comment in comments:
            comment_text = comment.text

            if '#admin' in comment_text.lower():
                parent_element_text = comment.find_element(By.XPATH, "./..").text
                if '\n' in parent_element_text:
                    combined_comment = ' '.join([comment_text, parent_element_text])
                    first_row = combined_comment.split('\n')[0]
                    print(first_row)
                else:
                    print(comment_text)

                # Download the image
                image_name = os.path.basename(link) + ".jpg"
                sanitized_image_name = sanitize_filename(image_name)
                image_path = os.path.join(r"C:\Users\ivanne bayer\Desktop\Computer Science\Comp Sci - Yr. 3 second sem\CS 3201 - Thesis 1\CS 3201 - Web Scraper BAYER\imgs", sanitized_image_name)

                csv_file_path = "C:\\Users\\ivanne bayer\\Desktop\\Computer Science\\Comp Sci - Yr. 3 second sem\\CS 3201 - Thesis 1\\CS 3201 - Web Scraper BAYER\\temp_post_ID.csv"

                with open(csv_file_path, 'r', newline='') as file:
                    csv_reader = csv.reader(file)
                    rows = list(csv_reader)
                    for row in rows:
                        if link in row:
                            row[2] = comment_text if first_row is None else first_row
                            break

                with open(csv_file_path, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerows(rows)

                if os.path.exists(image_path):
                    print("Image file already exists. Skipping...")
                    break

                with open(image_path, 'wb') as img_file:
                    img_file.write(requests.get(image_src).content)

        if comment_text is None:
            csv_file_path = "C:\\Users\\ivanne bayer\\Desktop\\Computer Science\\Comp Sci - Yr. 3 second sem\\CS 3201 - Thesis 1\\CS 3201 - Web Scraper BAYER\\temp_post_ID.csv"
            print("No comments in this post")
            
            with open(csv_file_path, 'r', newline='') as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
                for row in rows:
                    if link in row:
                        row[2] = "No comments in this post"
                        break

            with open(csv_file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(rows)

    except NoSuchElementException:
        print("Webpage does not exist")
        csv_file_path = "C:\\Users\\ivanne bayer\\Desktop\\Computer Science\\Comp Sci - Yr. 3 second sem\\CS 3201 - Thesis 1\\CS 3201 - Web Scraper BAYER\\temp_post_ID.csv"
        with open(csv_file_path, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)
            for row in rows:
                if link in row:
                    row[2] = "Webpage does not exist"
                    break

        with open(csv_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerows(rows)
    except Exception as e:
        print("An error occurred while saving comments or extracting image source:", e)

    

def sanitize_filename(filename):
    return re.sub(r'[^\w.]+', '', filename)



first_column_values = store_into_stack(8707, 10000)
iterate_the_links(first_column_values)