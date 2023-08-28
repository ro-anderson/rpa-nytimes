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

# Page Object Pattern Implementation
# Redefining the NYTBasePage class for context
class NYTBasePage:
    """Base class representing common functionalities for all NYT pages."""
    def __init__(self, browser):
        self.browser = browser
    def open_the_website(self, url):
        """
        Open the specified website URL in the browser.
        
        Args:
        - url (str): The website URL to open.
        
        Returns:
        - None
        """

        self.browser.open_available_browser(url)

    # Add other common methods here if needed

# Implementation of the HomePage class's search method based on tasks.py
class HomePage(NYTBasePage):
    """Represents the main page of the New York Times."""

    def __init__(self, browser):
        super().__init__(browser)
        self.url = "https://www.nytimes.com/"

    def search(self, search_term):
        """
        Search for a term on the NYT homepage.
        
        Args:
        - search_term (str): The term or phrase to search for.
        
        Returns:
        - None
        """
        # Placeholder for the actual search logic from tasks.py
        pass
    # Additional methods related to HomePage functionalities can be added here

    # Note: The actual implementations of the methods have been omitted and can be filled in using the code from tasks.py.


# Now, let's define the SearchResultsPage class
# Refining the SearchResultsPage class to include XPath selectors as class attributes

class SearchResultsPage(NYTBasePage):
    """Represents the search results page on the New York Times."""

    def __init__(self, browser, workitem, term, news_categories, number_of_months):
        super().__init__(browser)

        self.wi = workitem
        self.term = term
        self.news_categories = news_categories
        self.number_of_months = number_of_months
        self.wi.get_input_work_item() 
    
    # XPath selectors
    magnifier_button =  '//button[@data-testid="search-button"]'
    search_input_selector = '//*[@id="search-input"]/form/div/input'
    go_button = '//*[@id="search-input"]/form/button'
    multiselect_button = '//button[@data-testid="search-multiselect-button"]'
    multiselect_date_range_button = '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[1]/div/div/button'
    specific_dates_button = '//*[@id="site-content"]/div/div[1]/div[2]/div/div/div[1]/div/div/div/ul/li[6]/button'
    start_date_input_button = '//input[@data-testid="DateRange-startDate" and @id="startDate"]'
    end_date_input_button = '//input[@data-testid="DateRange-endDate" and @id="endDate"]'
    show_more_button = '//*[@id="site-content"]/div/div[2]/div[2]/div/button'
    xpath_categories = '//ul[@data-testid="multi-select-dropdown-list"]/li/label/span'
    # CSS selector for the cookie acceptance button
    cookies_acceptance_selector = '//button[@data-testid="GDPR-accept"]'
    # XPath selector for the terms update acceptance button
    terms_update_acceptance_selector = '//button[@class="css-1fzhd9j" and text()="Continue"]'    

    def get_available_categories(self):
        """Extracts all available categories from the dropdown list."""
        
        categories = [element.text for element in self.browser.get_webelements(self.xpath_categories)]

        # Remove numbers from each category name
        cleaned_categories = [re.sub(r'\d+', '', category) for category in categories]
        
        return cleaned_categories

    def get_valid_categories(self):
        """Checks if the provided categories are part of the available categories."""
        available_categories = self.get_available_categories()
        
        # Return only those categories from news_categories that exist in the available_categories
        valid_categories = [category for category in self.news_categories if category in available_categories]
        
        # Save output workitem - versioning valid categories
        self.wi.create_output_work_item({"valid_categories":valid_categories}, save=True)

        return valid_categories

    def check_categories(self):
        # Step 0: Filter out categories that are not present on the webpage
        valid_categories = self.get_valid_categories()    

        # If the resulting list is empty, only select 'Any'
        if not valid_categories:
            self.check_category("Any")
            return

        #elif contains 'Any', only select 'Any'
        elif "Any" in valid_categories:
            self.check_category("Any")
            return

        else:

            # Check and select each valid category in the list
            for category in valid_categories:
                self.check_category(category)
            return

    def check_category(self, news_category):

        # XPath to locate the checkbox based on the inner text of its corresponding label
        checkbox_xpath = f'//label[contains(., "{news_category}")]/input[@type="checkbox"]'
        
        # Check if the checkbox is already checked
        is_checked = self.browser.is_element_attribute_equal_to(checkbox_xpath, "checked", "true")
        
        # If the checkbox is not already checked, click on it
        if not is_checked:
            self.browser.click_element_when_clickable(checkbox_xpath)

    def calculate_search_dates_range(self) -> dict:
        """
        Calculates the search dates range based on the given number of months from today.

        Args:
        - number_of_months (int): The number of months for the range.

        Returns:
        - dict: Dictionary containing the start and end date of the range.
        """
        # Check if number_of_months is an integer and non-negative
        if not isinstance(self.number_of_months, int) or self.number_of_months < 0:
            raise ValueError("number_of_months must be a non-negative integer.")
        
        # Calculate the end date (which is today)
        end_date = datetime.date.today()
        
        # Calculate the start date
        if self.number_of_months == 0:
            start_date = datetime.date(end_date.year, end_date.month, 1)
        else:
            # Adjust the starting month
            month_adjustment = self.number_of_months - 1 if self.number_of_months > 1 else 0
            start_date = (end_date - relativedelta(months=month_adjustment)).replace(day=1)
        
        return {"start_date": start_date.strftime('%m/%d/%Y'), "end_date": end_date.strftime('%m/%d/%Y')}

    def close_modals(self):

        # Wait for and click the terms update acceptance button (if it appears)
        self.browser.click_element_when_clickable(self.terms_update_acceptance_selector, timeout=10)

        # Wait for and click the cookies acceptance button (if it appears)
        self.browser.click_element_when_clickable(self.cookies_acceptance_selector, timeout=10)

    def apply_filters(self):
        """
        Apply filters on the search results page to narrow down the articles based on criteria.
        
        Returns:
        - None
        """
        # Placeholder for the actual filter application logic from tasks.py

        # Close any modals that appear
        self.close_modals()

        # Click on magnifier button
        self.browser.click_element_when_clickable(self.magnifier_button, timeout=10)

        # Input the term into the search field using the browser
        self.browser.input_text_when_element_is_visible(self.search_input_selector, self.term)

        # Click on magnifier button
        self.browser.click_element_when_clickable(self.go_button, timeout=10)

        # Filter by date
        search_dates_range = self.calculate_search_dates_range()

        # Click on multiselect date range button button to Collapse
        self.browser.click_element_when_clickable(self.multiselect_date_range_button, timeout=10)

        # Click on specific dates
        self.browser.click_element_when_clickable(self.specific_dates_button, timeout=10)

        # Input the start_date 
        self.browser.input_text_when_element_is_visible(self.start_date_input_button, search_dates_range["start_date"])

        # Input date the end_date 
        self.browser.input_text_when_element_is_visible(self.end_date_input_button, search_dates_range["end_date"])

        # Click Enter
        self.browser.press_keys(self.end_date_input_button , "ENTER")
    
        # Click on magnifier button
        self.browser.click_element_when_clickable(self.multiselect_button, timeout=10)

        # Check checkbox category
        self.check_categories()

        # Click on magnifier button to Collapse
        self.browser.click_element_when_clickable(self.multiselect_button, timeout=10)

 

    def extract_articles(self):
        """
        Extract article details like title, date, and description from the search results page.
        
        Returns:
        - list: A list of dictionaries containing article details.
        """
        # Placeholder for the actual article extraction logic from tasks.py
        pass

    # Additional methods related to SearchResultsPage functionalities can be added here



# The class structure is now correctly defined.

if __name__ == '__main__':


    def get_work_item_data():

        # Load the current work item
        wi = WorkItems()
        wi.get_input_work_item() 
        input_wi = wi.get_work_item_variables() 
        print(input_wi['search_phrase']) 
        print(input_wi['news_categories'])
        print(input_wi['number_of_months'])

        return input_wi["search_phrase"], input_wi["news_categories"], input_wi["number_of_months"]

    term, news_categories, number_of_months = get_work_item_data()

    # Sample usage:
    browser = Selenium()
    workitem = WorkItems()
    home_page = HomePage(browser)
    home_page.open_the_website(home_page.url)
    search_results_page = SearchResultsPage(browser, workitem, term, news_categories, number_of_months)
    search_results_page.apply_filters()
    # search_results = SearchResultsPage(browser)
    # search_results.apply_filters()
    # search_results.extract_articles()

    # Note: The actual function implementations have been omitted and can be filled in as needed.

