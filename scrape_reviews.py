import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--log-level=3")
options.add_argument("--disable-infobars")
options.add_argument("--disable-notifications")
options.add_argument("--disable-popup-blocking")
options.add_argument("--start-maximized")


options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36"
)

driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(60)  

BASE_URL = "https://www.ratemyprofessors.com/professor/"


professors_reviews = []


professor_data = []
with open("professors_queens_college.csv", "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  
    for row in reader:
        professor_id, professor_name, department, rating = row  
        professor_data.append((professor_id, professor_name))


def scrape_professor_reviews(professor_id, prof_name):
    """Extracts course, timestamp, and user review for a given professor."""
    prof_url = f"{BASE_URL}{professor_id}"
    
    try:
        driver.get(prof_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Rating__StyledRating-sc-1rhvpxz-1"))
        )
    except TimeoutException:
        print(f"⏳ Timeout while loading {prof_name}'s page. Skipping...")
        return  

    try:
        review_elements = driver.find_elements(By.CLASS_NAME, "Rating__StyledRating-sc-1rhvpxz-1")

        if not review_elements:
            print(f"⚠️ No reviews found for {prof_name}. Skipping...")
            return

        for review in review_elements:
            try:
                
                course_name = "Unknown Course"
                try:
                    course_element = review.find_element(By.XPATH, ".//div[@class='RatingHeader__StyledClass-sc-1dlkqw1-3 eXfReS']")
                    if course_element:
                        course_name = course_element.text.strip()
                except NoSuchElementException:
                    print(f"⚠️ No course found for {prof_name}. Debugging: \n{review.get_attribute('innerHTML')}\n")

                
                review_date = "Unknown Date"
                try:
                    date_element = review.find_element(By.XPATH, ".//div[contains(@class, 'TimeStamp__StyledTimeStamp')]")
                    if date_element:
                        review_date = date_element.text.strip()
                except NoSuchElementException:
                    print(f"⚠️ No date found for {prof_name}. Debugging: \n{review.get_attribute('innerHTML')}\n")

                
                user_review = "No review text"
                try:
                    review_text_element = review.find_element(By.CLASS_NAME, "Comments__StyledComments-dzzyvm-0")
                    if review_text_element:
                        user_review = review_text_element.text.strip()
                except NoSuchElementException:
                    print(f"⚠️ No review text found for {prof_name}.")

                
                print(f"📌 Extracted for {prof_name} - Course: {course_name}, Date: {review_date}, Review: {user_review[:50]}...")

               
                professors_reviews.append([professor_id, prof_name, prof_url, course_name, review_date, user_review])
                print(f"📝 Saved review for {prof_name}: {course_name} - {review_date}")

            except (NoSuchElementException, IndexError):
                print(f"⚠️ Missing elements in a review for {prof_name}. Skipping...")

    except StaleElementReferenceException:
        print(f"⚠️ Stale element error while scraping {prof_name}. Retrying...")
        time.sleep(3)
        scrape_professor_reviews(professor_id, prof_name)


def save_to_csv():
    """ Save scraped reviews to CSV file. """
    review_file = "professors_reviews.csv"

    with open(review_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Professor ID", "Professor Name", "Profile URL", "Course", "Review Date", "Review"])
        writer.writerows(professors_reviews)

    print(f"✅ Saved {len(professors_reviews)} reviews to {review_file}.")


try:
    
    for prof_id, prof_name in professor_data:
        scrape_professor_reviews(prof_id, prof_name)

except KeyboardInterrupt:
    print("\n🛑 Scraping interrupted by user (Ctrl+C). Saving progress...")

finally:
    print("📁 Saving collected data before exiting...")
    save_to_csv()
    driver.quit()
    print("🚀 Scraper finished!")