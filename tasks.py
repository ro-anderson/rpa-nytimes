from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files

browser_lib = Selenium()
excel_lib = Files()

wi = WorkItems()

def get_work_item_data():

    # Load the current work item
    #wi = WorkItems()
    wi.get_input_work_item() 
    input_wi = wi.get_work_item_variables() 
    print(input_wi['search_phrase']) 
    print(input_wi['news_category'])
    print(input_wi['number_of_months'])

    return input_wi["search_phrase"], input_wi["news_category"]

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
    excel_lib.create_workbook(path="./output/news.xlsx", fmt="xlsx")

    # Append an existing Table object
    table = create_news_table()
    
    excel_lib.append_rows_to_worksheet(table, header=True)

    excel_lib.save_workbook("./output/news.xlsx")
    

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

def check_category(news_category):
    # XPath to locate the checkbox based on the inner text of its corresponding label
    checkbox_xpath = f'//label[contains(., "{news_category}")]/input[@type="checkbox"]'
    
    # Check if the checkbox is already checked using the new function
    is_checked = browser_lib.is_element_attribute_equal_to(checkbox_xpath, "checked", "true")
    
    # If the checkbox is not already checked, click on it
    if not is_checked:
        browser_lib.click_element_when_clickable(checkbox_xpath)

def search_for():
    term, news_category = get_work_item_data()

    # CSS selector for the search input based on its id //*[@id="app"]/div[2]/div[2]/header/section[1]/div[1]/div[2]/button
    magnifier_buttom =  '//button[@data-testid="search-button"]'
    search_input_selector = '//*[@id="search-input"]/form/div/input'
    go_buttom = '//*[@id="search-input"]/form/button'
    multiselect_button = '//button[@data-testid="search-multiselect-button"]'

    # Close any modals that appear
    close_modals()

    # Click on magnifier buttom
    browser_lib.click_element_when_clickable(magnifier_buttom, timeout=10)

    # Input the term into the search field using the browser_lib
    browser_lib.input_text_when_element_is_visible(search_input_selector, term)

    # Click on magnifier buttom
    browser_lib.click_element_when_clickable(go_buttom, timeout=10)

    # Click on magnifier buttom
    browser_lib.click_element_when_clickable(multiselect_button, timeout=10)

    # Check checkbox category
    check_category(news_category)

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