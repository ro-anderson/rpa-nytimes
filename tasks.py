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
        self.excel_file = Files()
        self.search_dates_range = self.calculate_search_dates_range()

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
    root_div_elements_css = "css:.css-1l4w6pd"
    date_locator = "17ubb9w"
    title_locator = "2fgx4k"
    description_locator = "16nhkrn"
    image_locator = "rq4mmj"
    directory_output_path = './output'

    def transform_article_data(self, list_articles: list) -> dict:
        """
        Transforms a list of article data dictionaries into a dictionary of lists using dictionary comprehension.
        
        Args:
        - list_articles (list): List of dictionaries, where each dictionary contains data for a single article.
        
        Returns:
        - dict: A dictionary where each key corresponds to a field (e.g., title, date) and each value is a list of all values for that field across all articles.
        """
        
        keys = ["title", "date", "description", "picture_filename", "contains_money_format_on_title_or_description", "count_search_phrases"]
        
        return {key: [article[key] for article in list_articles] for key in keys}

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
            if start_date <= datetime.datetime.strptime(self.text_to_formatted_date(article['date']), '%m/%d/%Y') <= end_date
        ]
        
        return filtered_articles

    def create_excel(self, list_articles):


        # Create modern format workbook with a path set.
        self.excel_file.create_workbook(path="./output/articles.xlsx", fmt="xlsx")

        # Append an existing Table object
        table = self.transform_article_data(list_articles)
        
        self.excel_file.append_rows_to_worksheet(table, header=True)

        self.excel_file.save_workbook("./output/articles.xlsx")

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

    def contains_money_format_on_title_or_description(self, title: str, description: str) -> bool:
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

    def download_image_with_uuid(self, image_url: str, directory_path: str) -> str:
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

    def safe_get_image_url(self, locator, parent=None):
        try:
            image_element = self.browser.find_element(locator, parent=parent)
            return self.browser.get_element_attribute(image_element, "src")
        except:
            return ''

    def safe_get_text(self, locator, parent=None):
        try:
            return self.browser.find_element(locator, parent=parent).text
        except:
            return ''

    def is_date_in_range(self, date):
        """
        Checks if a given date is within the specified date range.
        
        Args:
        - date (str): The date string in the format 'MM/DD/YYYY'.
        - search_dates_range (dict): Dictionary with 'start_date' and 'end_date' keys.
        
        Returns:
        - bool: True if the date is within the range, False otherwise.
        """
        start_date = datetime.datetime.strptime(self.search_dates_range['start_date'], '%m/%d/%Y')
        end_date = datetime.datetime.strptime(self.search_dates_range['end_date'], '%m/%d/%Y')
        current_date = datetime.datetime.strptime(date, '%m/%d/%Y')
        
        return start_date <= current_date <= end_date

    def text_to_formatted_date(self, date_text: str) -> str:
        # Dictionary for mapping non-standard month abbreviations
        month_abbr_mapping = {
            "Jan.": "January",
            "Feb.": "February",
            "Mar.": "March",
            "Apr.": "April",
            "May": "May",
            "June": "June",
            "July": "July",
            "Aug.": "August",
            "Sept.": "September",
            "Oct.": "October",
            "Nov.": "November",
            "Dec.": "December"
        }
        
        # Replace non-standard month abbreviations with standard ones
        date_text_cleaned = ' '.join([month_abbr_mapping.get(word, word) for word in date_text.split()])
        
        # If the date is in the format "Month Day", append the current year
        if re.match(r'^[A-Za-z]+\s+\d+$', date_text_cleaned):
            date_text_cleaned = f"{date_text_cleaned}, {datetime.datetime.now().year}"
        
        # Handle "Xh ago" format
        hours_ago_match = re.match(r'(\d+)h ago', date_text)
        if hours_ago_match:
            hours = int(hours_ago_match.group(1))
            date_obj = datetime.datetime.now() - datetime.timedelta(hours=hours)
            return date_obj.strftime('%m/%d/%Y')
        
        # Handle "Xm ago" format
        minutes_ago_match = re.match(r'(\d+)m ago', date_text)
        if minutes_ago_match:
            minutes = int(minutes_ago_match.group(1))
            date_obj = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
            return date_obj.strftime('%m/%d/%Y')
        
        try:
            # Try to parse the date using the full month name format
            date_obj = datetime.datetime.strptime(date_text_cleaned, '%B %d, %Y')
            
            # Convert the datetime object to a formatted string "MM-DD-YYYY"
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except:
            return date_text  # Return original date_text if there's an error

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
        self.browser.input_text_when_element_is_visible(self.search_input_selector, self.term)

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
            date = self.text_to_formatted_date(self.safe_get_text(f"css:.css-{self.date_locator}", parent=div))

            # If date is out of the range, skip the current iteration
            if not self.is_date_in_range(date):
                continue

            title = self.safe_get_text(f"css:.css-{self.title_locator}", parent=div)
            description = self.safe_get_text(f"css:.css-{self.description_locator}", parent=div)
            image_url = self.safe_get_image_url(f"css:.css-{self.image_locator}", parent=div)

            # download image by the url
            print(f"\nDownloading image with: date:{date}\ntitle:{title}\n")
            picture_filename = self.download_image_with_uuid(image_url, self.directory_output_path)

            # Storing data in a dictionary and appending to the list
            article_data = {
                "date": date,
                "title": title,
                "description": description,
                "picture_filename": picture_filename,
                "contains_money_format_on_title_or_description": self.contains_money_format_on_title_or_description(title, description),
                "count_search_phrases": self.count_search_phrases(title, description, term)
            }
            articles_data.append(article_data)

        # As the datetime filter of nytimes is not working as expected, we need to filter the articles for the data range that we want
        filtred_articles = self.filter_articles_by_search_dates_range(articles_data)

        self.create_excel(filtred_articles)

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
    search_results_page.extract_articles()

