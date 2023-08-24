from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
import re
import datetime

browser_lib = Selenium()
excel_lib = Files()

wi = WorkItems()

def calculate_date_range(number_of_months):
    # Check if number_of_months is an integer and greater than 0
    if not isinstance(number_of_months, int) or number_of_months < 0:
        raise ValueError("number_of_months must be an integer greater than 0.")

    # Adust to M - 1
    if number_of_months > 0:
        number_of_months = number_of_months - 1 
    
    # Calculate the total number of months from 01/01/1851 to today
    start_date_1851 = datetime.date(1851, 1, 1)
    today = datetime.date.today()
    delta = today - start_date_1851
    total_months = (delta.days // 30)  # Approximate month as 30 days for simplicity
    
    # Set the upper limit for number_of_months
    if number_of_months > total_months:
        number_of_months = total_months

    # Calculate the start date
    end_date = today
    year_change = (today.month - number_of_months) <= 0  # Check if we need to subtract a year
    start_month = (today.month - number_of_months + 12) % 12 or 12  # Handle December separately
    start_year = today.year - year_change
    start_date = datetime.date(start_year, start_month, 1)
    
    return {"start_date": start_date.strftime('%m/%d/%Y'), "end_date": end_date.strftime('%m/%d/%Y')}

def get_work_item_data():

    # Load the current work item
    wi.get_input_work_item() 
    input_wi = wi.get_work_item_variables() 
    print(input_wi['search_phrase']) 
    print(input_wi['news_categories'])
    print(input_wi['number_of_months'])

    return input_wi["search_phrase"], input_wi["news_categories"], input_wi["number_of_months"]


def create_news_table():
    table = {
        "title": ["Sample News Headline 1", "Sample News Headline 2", "Sample News Headline 3"],
        "date": ["2023-08-23", "2023-08-22", "2023-08-21"],
        "description": [
            "This is a description for Sample News 1.",
            "This is a description for Sample News 2.",
            "This is a description for Sample News 3."
        ],
        "picture": [
            "path/to/image1.jpg",
            "path/to/image2.jpg",
            "path/to/image3.jpg"
        ]
    }
    return table

def create_excel():


    # Create modern format workbook with a path set.
    excel_lib.create_workbook(path="./output/articles.xlsx", fmt="xlsx")

    # Append an existing Table object
    table = create_news_table()
    
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


    # Close any modals that appear
    close_modals()

    # Click on magnifier button
    browser_lib.click_element_when_clickable(magnifier_button, timeout=10)

    # Input the term into the search field using the browser_lib
    browser_lib.input_text_when_element_is_visible(search_input_selector, term)

    # Click on magnifier button
    browser_lib.click_element_when_clickable(go_button, timeout=10)

    # Filter by date
    search_dates_range = calculate_date_range(number_of_months)

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

    # get title
    
    # Click on magnifier button
    browser_lib.click_element_when_clickable(multiselect_button, timeout=10)

    # Check checkbox category
    check_categories(news_categories)

    # Click on magnifier button to Collapse
    browser_lib.click_element_when_clickable(multiselect_button, timeout=10)

# Define a main() function that calls the other functions in order:
def main():
    try:
        open_the_website("https://www.nytimes.com/")
        search_for()
        create_excel()
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()