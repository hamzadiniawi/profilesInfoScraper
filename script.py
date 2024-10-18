from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
import openpyxl

# Function to extract profile meta description information and address
def extract_profile_info(driver, username):
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)  # Allow time for the profile to load

    try:
        # Locate the meta description tag
        meta_description = driver.find_element(By.XPATH, '//meta[@name="description"]')
        meta_content = meta_description.get_attribute("content")

        # Clean up the extracted text
        cleaned_text = re.sub(r'\s+', ' ', meta_content)  # Replace multiple spaces with a single space
        cleaned_text = remove_duplicates(cleaned_text)  # Remove duplicate segments

        # Try to extract the text content of the first <h1> element within <header>
        header = driver.find_element(By.XPATH, '//header')
        h1_elements = header.find_elements(By.TAG_NAME, 'h1')
        address_text = h1_elements[0].text if h1_elements else ""

    except Exception as e:
        print(f"Error extracting data for {username}: {e}")
        cleaned_text = "No data found"
        address_text = ""

    return {
        "Username": username,
        "Meta Description": cleaned_text,
        "Address": address_text
    }

def remove_duplicates(text):
    """Remove duplicate segments in a string separated by '|'"""
    segments = [segment.strip() for segment in text.split('|')]
    seen = set()
    unique_segments = [segment for segment in segments if not (segment in seen or seen.add(segment))]
    return ' | '.join(unique_segments)

# Main function to process usernames
def process_usernames(driver, csv_file):
    # Load usernames from CSV with UTF-8 encoding
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    print("CSV Columns:", df.columns)  # Print columns to verify the correct name

    # Adjust column name as per your CSV file
    username_column = "Username"  # Change this if your column name is different

    if username_column not in df.columns:
        raise ValueError(f"Column '{username_column}' not found in CSV file.")

    usernames = df[username_column].tolist()

    # Load or create Excel file
    try:
        workbook = openpyxl.load_workbook("instagram_profiles_info.xlsx")
        sheet = workbook.active
    except FileNotFoundError:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["Username", "Meta Description", "Address"])

    # Process each username
    for username in usernames:
        print(f"Processing profile: {username}")
        profile_info = extract_profile_info(driver, username)

        # Append the new data to the Excel file
        sheet.append([profile_info["Username"], profile_info["Meta Description"], profile_info["Address"]])

        # Save the Excel file after processing each username
        workbook.save("instagram_profiles_info.xlsx")
        print(f"Data for '{username}' saved to instagram_profiles_info.xlsx")
        time.sleep(20)  # Pause to avoid being blocked

# Initialize WebDriver and navigate to Instagram login page
driver = webdriver.Chrome()  # Ensure the path to chromedriver is correct
driver.get("https://www.instagram.com/accounts/login/")
print("Please log in manually. Once logged in, press Enter here to continue...")

input("Press Enter to continue after logging in...")

# Continue with processing
csv_file = "instagram_profiles.csv"
process_usernames(driver, csv_file)

# Close the browser
driver.quit()
