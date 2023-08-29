from RPA.Robocorp.WorkItems import WorkItems
import re
import datetime
from time import sleep
import logging
from src.utility import Utility
from src.excel_handler import ExcelHandler
import json

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

class HomePage(NYTBasePage):
    """Represents the main page of the New York Times."""

    def __init__(self, browser):
        super().__init__(browser)
        self.url = "https://www.nytimes.com/"

class SearchResultsPage(NYTBasePage):
    """Represents the search results page on the New York Times."""
    def __init__(self, browser):
        super().__init__(browser)
        self.utils = Utility(browser)

        self.wi = WorkItems()
        self.wi.get_input_work_item()
        self.input_wi = self.wi.get_work_item_variables() 
        self.search_phrase = self.input_wi["search_phrase"]
        self.news_categories = self.input_wi["news_categories"]
        self.number_of_months = self.input_wi["number_of_months"]
        self.excel_handler = ExcelHandler()
        
        self.search_dates_range = self.utils.calculate_search_dates_range(self.number_of_months)
        self.config = self.load_config()

        # Extracting selectors and other configurations from the config dictionary
        self.magnifier_button = self.config["selectors"]["magnifier_button"]
        self.search_input_selector = self.config["selectors"]["search_input_selector"]
        self.go_button = self.config["selectors"]["go_button"]
        self.multiselect_button = self.config["selectors"]["multiselect_button"]
        self.multiselect_date_range_button = self.config["selectors"]["multiselect_date_range_button"]
        self.specific_dates_button = self.config["selectors"]["specific_dates_button"]
        self.start_date_input_button = self.config["selectors"]["start_date_input_button"]
        self.end_date_input_button = self.config["selectors"]["end_date_input_button"]
        self.show_more_button = self.config["selectors"]["show_more_button"]
        self.xpath_categories = self.config["selectors"]["xpath_categories"]
        self.cookies_acceptance_selector = self.config["selectors"]["cookies_acceptance_selector"]
        self.terms_update_acceptance_selector = self.config["selectors"]["terms_update_acceptance_selector"]
        self.root_div_elements_css = self.config["selectors"]["root_div_elements_css"]
        self.date_locator = self.config["selectors"]["date_locator"]
        self.title_locator = self.config["selectors"]["title_locator"]
        self.description_locator = self.config["selectors"]["description_locator"]
        self.image_locator = self.config["selectors"]["image_locator"]

        # Getting other configurations
        self.directory_output_path = self.config["output_directory"]

    def load_config(self, filename="config.json"):
        with open(filename, 'r') as file:
            config = json.load(file)
        return config

    def filter_articles_by_search_dates_range(self, articles):
        """
        Filters articles based on a given date range.
        
        Args:
        - articles (list): List of article dictionaries.
        - search_dates_range (dict): Dictionary with 'start_date' and 'end_date' keys.
        
        Returns:
        - list: Filtered list of articles.
        """
        
        # Convert the start_date and end_date strings to datetime objects
        start_date = datetime.datetime.strptime(self.search_dates_range['start_date'], '%m/%d/%Y')
        end_date = datetime.datetime.strptime(self.search_dates_range['end_date'], '%m/%d/%Y')
        
        # Filter the articles based on the date range
        filtered_articles = [
            article for article in articles
            if start_date <= datetime.datetime.strptime(self.utils.text_to_formatted_date(article['date']), '%m/%d/%Y') <= end_date
        ]
        
        return filtered_articles

    def count_search_phrases(self, title: str, description: str, term: str) -> int:
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


    def close_modals_updated(self):
        """Close modals that might appear during page interactions."""
        try:
            # Wait for and click the terms update acceptance button (if it appears)
            self.browser.click_element_when_clickable(self.terms_update_acceptance_selector, timeout=15)

        except Exception as e:  # Catch all exceptions to be safe, but you can specify the exact exception type if desired
            # If the modal doesn't appear within the timeout, just log a message and continue
            print(f"Modal did not appear or could not be closed: {e}")

    def close_modals(self):
        """Close modals that might appear during page interactions."""
        try:
            # Wait for and click the terms update acceptance button (if it appears)
            self.browser.click_element_when_clickable(self.terms_update_acceptance_selector, timeout=15)
        except Exception as e:
            # If the modal doesn't appear within the timeout, just log a message and continue
            print(f"Terms update acceptance modal did not appear or could not be closed: {e}")

        try:
            # Wait for and click the cookies acceptance button (if it appears)
            self.browser.click_element_when_clickable(self.cookies_acceptance_selector, timeout=10)
        except Exception as e:
            # If the modal doesn't appear within the timeout, just log a message and continue
            print(f"Cookies acceptance modal did not appear or could not be closed: {e}")

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
        self.browser.input_text_when_element_is_visible(self.search_input_selector, self.search_phrase)

        # Click on magnifier button
        self.browser.click_element_when_clickable(self.go_button, timeout=10)

        # Click on multiselect date range button button to Collapse
        self.browser.click_element_when_clickable(self.multiselect_date_range_button, timeout=10)

        # Click on specific dates
        self.browser.click_element_when_clickable(self.specific_dates_button, timeout=10)

        # Input the start_date 
        self.browser.input_text_when_element_is_visible(self.start_date_input_button, self.search_dates_range["start_date"])

        # Input date the end_date 
        self.browser.input_text_when_element_is_visible(self.end_date_input_button, self.search_dates_range["end_date"])

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
        while True:
            try:
                # Wait until the "SHOW MORE" button is clickable and click on it
                self.browser.click_element_when_clickable(show_more_button, timeout=2)

            except:
                # If the "SHOW MORE" button is not found or not clickable within the timeout period, break out of the loop
                break

        # get data
        articles_data = []

        # Locate all root div elements for articles based on a structure commonality.
        article_divs = self.browser.find_elements(self.root_div_elements_css)

        for div in article_divs:

            # Use the helper function
            date = self.utils.text_to_formatted_date(self.utils.safe_get_text(f"css:.css-{self.date_locator}", parent=div))

            # If date is out of the range, skip the current iteration
            if not self.utils.is_date_in_range(date, self.search_dates_range):
                continue

            title = self.utils.safe_get_text(f"css:.css-{self.title_locator}", parent=div)
            description = self.utils.safe_get_text(f"css:.css-{self.description_locator}", parent=div)
            image_url = self.utils.safe_get_image_url(f"css:.css-{self.image_locator}", parent=div)

            # download image by the url
            print(f"\nDownloading image with: date:{date}\ntitle:{title}\n")
            picture_filename = self.utils.download_image_with_uuid(image_url, self.directory_output_path)

            # Storing data in a dictionary and appending to the list
            article_data = {
                "date": date,
                "title": title,
                "description": description,
                "picture_filename": picture_filename,
                "contains_money_format_on_title_or_description": self.utils.contains_money_format_on_title_or_description(title, description),
                "count_search_phrases": self.utils.count_search_phrases(title, description, self.search_phrase)
            }
            articles_data.append(article_data)

        # As the datetime filter of nytimes is not working as expected, we need to filter the articles for the data range that we want
        filtred_articles = self.filter_articles_by_search_dates_range(articles_data)
        self.excel_handler.create_excel(filtred_articles)