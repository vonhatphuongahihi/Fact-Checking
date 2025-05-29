from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from time import sleep
import random
import os

def setup_driver():
    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-notifications')  # Disable notifications
    chrome_options.add_argument('--start-maximized')  # Start maximized
    
    # Setup ChromeDriver service
    service = Service("./chromedriver.exe")
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser

def login_facebook(browser, email, password):
    # Open Facebook
    browser.get("http://facebook.com")
    sleep(random.randint(2, 3))

    # Fill in login credentials
    txtUser = browser.find_element(By.ID, "email")
    txtUser.send_keys(email)

    txtPass = browser.find_element(By.ID, "pass")
    txtPass.send_keys(password)

    # Submit form
    txtPass.send_keys(Keys.ENTER)
    sleep(random.randint(2, 3))

def extract_comments(browser, post_url):
    # Open post URL
    browser.get(post_url)
    sleep(random.randint(4, 5))
    
    print(f"Processing post: {post_url}")
    
    # Try to load more comments
    count = 0
    for _ in range(10):  # Try up to 10 times
        try:
            show_more_comment = browser.find_element(By.XPATH, "//div[contains(@role, 'button') and contains(text(), 'Xem thêm bình luận')]")
            show_more_comment.click()
            sleep(random.randint(4, 6))
        except WebDriverException:
            count += 1
            sleep(random.randint(2, 3))
            continue
    
    # Find all comments
    comment_list = browser.find_elements(By.XPATH, '//div[@role="article"]')
    
    # Extract comment text
    comments = []
    for comment in comment_list:
        try:
            poster = comment.find_element(By.CLASS_NAME, "x1ye3gou")
            comment_text = poster.text.split('\n  ·\nTheo dõi\n')
            if len(comment_text) < 2:
                comment_text = comment_text[0].split('\n')
            comments.append(comment_text[-1])
        except:
            continue
    
    return comments

def main():
    # Your Facebook credentials
    EMAIL = "your_email@example.com"
    PASSWORD = "your_password"
    
    # List of post URLs to crawl
    post_urls = [
        "https://www.facebook.com/share/v/1Kn996Pp3g",
        "https://www.facebook.com/groups/timhieulichsu.thls/permalink/7229862700405367/?rdid=WnOdrAjZ6GQP1mdP#",
        "https://www.facebook.com/groups/timhieulichsu.thls/permalink/4494518903939774/?rdid=k8TDbPUouZS7CVjy#",
        "https://www.facebook.com/groups/timhieulichsu.thls/permalink/9946247905433486/?rdid=bMaGhz3ZNcyDl7dW#",
        "https://www.facebook.com/groups/timhieulichsu.thls/permalink/9389159531142329/?rdid=eMID0yM4O3hbJrYa#",
        "https://www.facebook.com/share/p/15F1DrqrgT",
        "https://www.facebook.com/share/p/1AgFDdfsGj",
        "https://www.facebook.com/share/p/19EFs5MLUr"
    ]
    
    try:
        # Setup browser
        browser = setup_driver()
        
        # Login to Facebook
        login_facebook(browser, EMAIL, PASSWORD)
        
        # Create output directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Process each post
        for post_url in post_urls:
            comments = extract_comments(browser, post_url)
            
            # Save comments to file
            with open('data.txt', "a", encoding="utf-8") as file:
                for comment in comments:
                    file.write(comment + "\n")
            
            sleep(random.randint(4, 7))
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        # Close browser
        browser.close()

if __name__ == "__main__":
    main()
