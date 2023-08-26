from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
import re
import datetime
from time import sleep
import logging
import uuid
import os
import urllib
from dateutil.relativedelta import relativedelta

browser_lib = Selenium()
excel_lib = Files()

wi = WorkItems()

def is_date_in_range(date,search_dates_range):
    """
    Checks if a given date is within the specified date range.
    
    Args:
    - date (str): The date string in the format 'MM/DD/YYYY'.
    - search_dates_range (dict): Dictionary with 'start_date' and 'end_date' keys.
    
    Returns:
    - bool: True if the date is within the range, False otherwise.
    """
    start_date = datetime.datetime.strptime(search_dates_range['start_date'], '%m/%d/%Y')
    end_date = datetime.datetime.strptime(search_dates_range['end_date'], '%m/%d/%Y')
    current_date = datetime.datetime.strptime(date, '%m/%d/%Y')
    
    return start_date <= current_date <= end_date


def filter_articles_by_search_dates_range(articles, search_dates_range):
    """
    Filters articles based on a given date range.
    
    Args:
    - articles (list): List of article dictionaries.
    - search_dates_range (dict): Dictionary with 'start_date' and 'end_date' keys.
    
    Returns:
    - list: Filtered list of articles.
    """
    
    # Convert the start_date and end_date strings to datetime objects
    start_date = datetime.datetime.strptime(search_dates_range['start_date'], '%m/%d/%Y')
    end_date = datetime.datetime.strptime(search_dates_range['end_date'], '%m/%d/%Y')
    
    # Filter the articles based on the date range
    filtered_articles = [
        article for article in articles
        if start_date <= datetime.datetime.strptime(text_to_formatted_date(article['date']), '%m/%d/%Y') <= end_date
    ]
    
    return filtered_articles

def transform_article_data(list_articles: list) -> dict:
    """
    Transforms a list of article data dictionaries into a dictionary of lists using dictionary comprehension.
    
    Args:
    - list_articles (list): List of dictionaries, where each dictionary contains data for a single article.
    
    Returns:
    - dict: A dictionary where each key corresponds to a field (e.g., title, date) and each value is a list of all values for that field across all articles.
    """
    
    keys = ["title", "date", "description", "picture_filename", "contains_money_format_on_title_or_description", "count_search_phrases"]
    
    return {key: [article[key] for article in list_articles] for key in keys}


def count_search_phrases(title: str, description: str, term: str) -> int:
    """
    Counts the occurrences of the search phrase (term) in the title and description.
    
    Args:
    - title (str): The article title.
    - description (str): The article description.
    - term (str): The search phrase.
    
    Returns:
    - int: The total count of the search phrase in the title and description.
    """
    
    # Counting occurrences of term in both title and description
    count_in_title = title.lower().count(term.lower())
    count_in_description = description.lower().count(term.lower())
    
    return count_in_title + count_in_description


def contains_money_format_on_title_or_description(title: str, description: str) -> bool:
    """
    Checks if the title or description contains any specified money format.
    
    Args:
    - title (str): The article title.
    - description (str): The article description.
    
    Returns:
    - bool: True if any money format is found, False otherwise.
    """
    
    # Define a regex pattern to match the specified money formats
    money_pattern = r"(\$[\d,]+(\.\d{1,2})?)|(\d+\s(dollars|USD))"
    
    # Search the pattern in the title and description
    if re.search(money_pattern, title) or re.search(money_pattern, description):
        return True
    return False

def download_image_with_uuid(image_url: str, directory_path: str) -> str:
    """
    Download the image from the given URL and save it with a UUID-based filename.
    
    Args:
    - image_url (str): The URL of the image to be downloaded.
    - directory_path (str): The directory where the image will be saved.
    
    Returns:
    - str: The path of the downloaded image.
    """

    
    
    # Generate a unique filename using UUID
    filename = str(uuid.uuid4()) + ".jpg"
    filepath = os.path.join(directory_path, filename)

    # Download the image
    if image_url:
        urllib.request.urlretrieve(image_url, filepath)
    else:
        return ''

    return filename

def extract_image_url(div_element) -> str:
    """
    Extract the image URL from the given article div element.
    
    Args:
    - div_element (WebElement): The article div element containing the image tag.
    
    Returns:
    - str: The extracted image URL or None if not found.
    """
    
    # Initialize browser lib
    browser_lib = Selenium()
    
    try:
        # Locate the image element within the article
        image_element = browser_lib.find_element("css:img.css-rq4mmj", parent=div_element)
        image_url = browser_lib.get_element_attribute(image_element, "src")
        return image_url
    except:
        return None

def safe_get_text(locator, parent=None):
    try:
        return browser_lib.find_element(locator, parent=parent).text
    except:
        return ''

def safe_get_image_url(locator, parent=None):
    try:
        image_element = browser_lib.find_element(locator, parent=parent)
        return browser_lib.get_element_attribute(image_element, "src")
    except:
        return ''

def text_to_formatted_date(date_text: str) -> str:
    # Dictionary for mapping non-standard month abbreviations
    month_abbr_mapping = {
        "Jan.": "January",
        "Feb.": "February",
        "Mar.": "March",
        "Apr.": "April",
        "May": "May",    # Even though "May" is standard, including it for completeness
        "June": "June",
        "July": "July",
        "Aug.": "August",
        "Sept.": "September",
        "Oct.": "October",
        "Nov.": "November",
        "Dec.": "December"
    }
    
    # Replace non-standard month abbreviations with standard ones using dictionary comprehension
    date_text_cleaned = ' '.join([month_abbr_mapping.get(word, word) for word in date_text.split()])
    
    try:
        # Try to parse the date using the full month name format
        date_obj = datetime.datetime.strptime(date_text_cleaned, '%B %d, %Y')
        
        # Convert the datetime object to a formatted string "MM-DD-YYYY"
        formatted_date = date_obj.strftime('%m/%d/%Y')
        return formatted_date
    except:
        return date_text  # Return original date_text if there's an error

def calculate_search_dates_range(number_of_months: int) -> dict:
    """
    Calculates the search dates range based on the given number of months from today.

    Args:
    - number_of_months (int): The number of months for the range.

    Returns:
    - dict: Dictionary containing the start and end date of the range.
    """
    # Check if number_of_months is an integer and non-negative
    if not isinstance(number_of_months, int) or number_of_months < 0:
        raise ValueError("number_of_months must be a non-negative integer.")
    
    # Calculate the end date (which is today)
    end_date = datetime.date.today()
    
    # Calculate the start date
    if number_of_months == 0:
        start_date = datetime.date(end_date.year, end_date.month, 1)
    else:
        # Adjust the starting month
        month_adjustment = number_of_months - 1 if number_of_months > 1 else 0
        start_date = (end_date - relativedelta(months=month_adjustment)).replace(day=1)
    
    return {"start_date": start_date.strftime('%m/%d/%Y'), "end_date": end_date.strftime('%m/%d/%Y')}

def get_work_item_data():

    # Load the current work item
    wi.get_input_work_item() 
    input_wi = wi.get_work_item_variables() 
    print(input_wi['search_phrase']) 
    print(input_wi['news_categories'])
    print(input_wi['number_of_months'])

    return input_wi["search_phrase"], input_wi["news_categories"], input_wi["number_of_months"]

def create_excel(list_articles):


    # Create modern format workbook with a path set.
    excel_lib.create_workbook(path="./output/articles.xlsx", fmt="xlsx")

    # Append an existing Table object
    table = transform_article_data(list_articles)
    
    excel_lib.append_rows_to_worksheet(table, header=True)

    excel_lib.save_workbook("./output/articles.xlsx")
    

def open_the_website(url):
    browser_lib.open_available_browser(url)

def close_modals():
    # CSS selector for the cookie acceptance button
    cookies_acceptance_selector = '//button[@data-testid="GDPR-accept"]'

    # XPath selector for the terms update acceptance button
    terms_update_acceptance_selector = '//button[@class="css-1fzhd9j" and text()="Continue"]'


    # Wait for and click the terms update acceptance button (if it appears)
    browser_lib.click_element_when_clickable(terms_update_acceptance_selector, timeout=10)

    # Wait for and click the cookies acceptance button (if it appears)
    browser_lib.click_element_when_clickable(cookies_acceptance_selector, timeout=10)

def get_available_categories():
    """Extracts all available categories from the dropdown list and removes numbers from the names."""
    xpath_categories = '//ul[@data-testid="multi-select-dropdown-list"]/li/label/span'
    categories = [element.text for element in browser_lib.get_webelements(xpath_categories)]
    
    # Remove numbers from each category name
    cleaned_categories = [re.sub(r'\d+', '', category) for category in categories]
    
    return cleaned_categories

def get_available_categories():
    """Extracts all available categories from the dropdown list."""
    xpath_categories = '//ul[@data-testid="multi-select-dropdown-list"]/li/label/span'
    categories = [element.text for element in browser_lib.get_webelements(xpath_categories)]

    # Remove numbers from each category name
    cleaned_categories = [re.sub(r'\d+', '', category) for category in categories]
    
    return cleaned_categories

def get_valid_categories(news_categories):
    """Checks if the provided categories are part of the available categories."""
    available_categories = get_available_categories()
    
    # Return only those categories from news_categories that exist in the available_categories
    valid_categories = [category for category in news_categories if category in available_categories]
    
    # Save output workitem - versioning valid categories
    wi.create_output_work_item({"valid_categories":valid_categories}, save=True)

    return valid_categories

def check_categories(news_categories):
    # Step 0: Filter out categories that are not present on the webpage
    valid_categories = get_valid_categories(news_categories)    

    # If the resulting list is empty, only select 'Any'
    if not valid_categories:
        check_category("Any")
        return

    #elif contains 'Any', only select 'Any'
    elif "Any" in valid_categories:
        check_category("Any")
        return

    else:

        # Check and select each valid category in the list
        for category in valid_categories:
            check_category(category)
        return

def check_category(news_category):
    # XPath to locate the checkbox based on the inner text of its corresponding label
    checkbox_xpath = f'//label[contains(., "{news_category}")]/input[@type="checkbox"]'
    
    # Check if the checkbox is already checked
    is_checked = browser_lib.is_element_attribute_equal_to(checkbox_xpath, "checked", "true")
    
    # If the checkbox is not already checked, click on it
    if not is_checked:
        browser_lib.click_element_when_clickable(checkbox_xpath)

def search_for():
    term, news_categories, number_of_months = get_work_item_data()

    # CSS selector for the search input based on its id
    magnifier_button =  '//button[@data-testid="search-button"]'
    search_input_selector = '//*[@id="search-input"]/form/div/input'
    go_button = '//*[@id="search-input"]/form/button'
    multiselect_button = '//button[@data-testid="search-multiselect-button"]'
    multiselect_date_range_button = '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[1]/div/div/button'
    specific_dates_button = '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[1]/div/div/div/ul/li[6]/button'
    start_date_input_button = '//input[@data-testid="DateRange-startDate" and @id="startDate"]'
    end_date_input_button = '//input[@data-testid="DateRange-endDate" and @id="endDate"]'
    show_more_button = '//*[@id="site-content"]/div/div[2]/div[2]/div/button'


    # Close any modals that appear
    close_modals()

    # Click on magnifier button
    browser_lib.click_element_when_clickable(magnifier_button, timeout=10)

    # Input the term into the search field using the browser_lib
    browser_lib.input_text_when_element_is_visible(search_input_selector, term)

    # Click on magnifier button
    browser_lib.click_element_when_clickable(go_button, timeout=10)

    # Filter by date
    search_dates_range = calculate_search_dates_range(number_of_months)

    # Click on multiselect date range button button to Collapse
    browser_lib.click_element_when_clickable(multiselect_date_range_button, timeout=10)

    # Click on specific dates
    browser_lib.click_element_when_clickable(specific_dates_button, timeout=10)

    # Input the start_date 
    browser_lib.input_text_when_element_is_visible(start_date_input_button, search_dates_range["start_date"])

    # Input date the end_date 
    browser_lib.input_text_when_element_is_visible(end_date_input_button, search_dates_range["end_date"])

    # Click Enter
    browser_lib.press_keys(end_date_input_button , "ENTER")
    
    # Click on magnifier button
    browser_lib.click_element_when_clickable(multiselect_button, timeout=10)

    # Check checkbox category
    check_categories(news_categories)

    # Click on magnifier button to Collapse
    browser_lib.click_element_when_clickable(multiselect_button, timeout=10)

    # Show all the news
    while True:
        try:
            # Wait until the "SHOW MORE" button is clickable and click on it
            browser_lib.click_element_when_clickable(show_more_button, timeout=2)
            
            # Introduce a small delay to allow content to load, say 2 seconds (optional but can be helpful)
            #sleep(2)
            
        except:
            # If the "SHOW MORE" button is not found or not clickable within the timeout period, break out of the loop
            break

    # get data
    articles_data = []

    # Locate all root div elements for articles based on a structure commonality.
    article_divs = browser_lib.find_elements("css:.css-1l4w6pd")
    # css pattern for mainliy elements
    date_locator = "17ubb9w"
    title_locator = "2fgx4k"
    description_locator = "16nhkrn"
    image_locator = "rq4mmj"

    for div in article_divs:

        # Use the helper function
        date = text_to_formatted_date(safe_get_text(f"css:.css-{date_locator}", parent=div))

        # If date is out of the range, skip the current iteration
        if not is_date_in_range(date, search_dates_range):
            continue

        title = safe_get_text(f"css:.css-{title_locator}", parent=div)
        description = safe_get_text(f"css:.css-{description_locator}", parent=div)
        image_url = safe_get_image_url(f"css:.css-{image_locator}", parent=div)

        # download image by the url
        directory_path = './output'
        picture_filename = download_image_with_uuid(image_url, directory_path)

        # Storing data in a dictionary and appending to the list
        article_data = {
            "date": date,
            "title": title,
            "description": description,
            "picture_filename": picture_filename,
            "contains_money_format_on_title_or_description": contains_money_format_on_title_or_description(title, description),
            "count_search_phrases": count_search_phrases(title, description, term)
        }
        articles_data.append(article_data)

    # As the datetime filter of nytimes is not working as expected, we need to filter the articles for the data range that we want
    filtred_articles = filter_articles_by_search_dates_range(articles_data, calculate_search_dates_range(number_of_months))
    

    return filtred_articles 


# Define a main() function that calls the other functions in order:
def main():
    try:
        open_the_website("https://www.nytimes.com/")
        articles_data = search_for()
        create_excel(articles_data)
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()