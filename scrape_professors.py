import csv
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0")

def create_driver():
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.ratemyprofessors.com/search/professors/231?q=*")
    wait = WebDriverWait(driver, 10)
    return driver, wait

def save_to_csv(data):
    with open("professors_queens_college.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Professor ID", "Name", "Department", "Rating"])
        writer.writerows(data)
    print(f"✅ Saved {len(data)} professors.")

driver, wait = create_driver()
professors = []
seen_professor_ids = set()
MAX_CLICKS = 1000
click_count = 0
no_new_data_count = 0
max_no_data_retries = 5

try:
    while click_count < MAX_CLICKS:
        try:
            wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "TeacherCard__StyledTeacherCard-syjs0d-0")))
        except TimeoutException:
            print("⚠️ Timeout waiting for professor cards.")
            break

        cards = driver.find_elements(By.CLASS_NAME, "TeacherCard__StyledTeacherCard-syjs0d-0")
        current_total = len(seen_professor_ids)
        print(f"📄 Found {len(cards)} cards on page...")

        for prof in cards:
            try:
                href = prof.get_attribute("href")
                if not href or "/professor/" not in href:
                    continue
                pid = href.split("/")[-1]
                if pid in seen_professor_ids:
                    continue

                name = prof.find_element(By.CLASS_NAME, "CardName__StyledCardName-sc-1gyrgim-0").text.strip()
                dept = prof.find_element(By.CLASS_NAME, "CardSchool__Department-sc-19lmz2k-0").text.strip()
                try:
                    rating = prof.find_element(By.CLASS_NAME, "CardNumRating__CardNumRatingNumber-sc-17t4b9u-2").text.strip()
                except:
                    rating = "N/A"

                professors.append([pid, name, dept, rating])
                seen_professor_ids.add(pid)
                print(f"✅ {name} - {dept} - {rating}")
            except Exception as e:
                continue

        if len(seen_professor_ids) == current_total:
            no_new_data_count += 1
            print("⚠️ No new data this round.")
        else:
            no_new_data_count = 0

        print(f"📊 Total unique professors: {len(seen_professor_ids)}")

        if no_new_data_count >= max_no_data_retries:
            print("🛑 Stopped due to no new data after multiple tries.")
            break

        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.5, 3.0))

            show_more = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "PaginationButton__StyledPaginationButton-txi1dr-1")))
            driver.execute_script("arguments[0].click();", show_more)
            click_count += 1
            print(f"🔄 Clicked Show More ({click_count}/{MAX_CLICKS})")

            # Variable sleep
            time.sleep(random.uniform(4.0, 8.5))

            # Occasional long sleep
            if click_count % random.randint(7, 12) == 0:
                print("😴 Taking a longer break to avoid detection...")
                time.sleep(random.uniform(20, 30))

        except (TimeoutException, NoSuchElementException):
            print("✅ No more pages or 'Show More' button.")
            break


except KeyboardInterrupt:
    print("🛑 Interrupted manually.")

finally:
    save_to_csv(professors)
    driver.quit()
    print("🚀 Scraping complete.")
