import uuid
import os
import urllib
from dateutil.relativedelta import relativedelta
import datetime
import re

class Utility:
    """
    A utility class containing helper functions for various operations.
    """

    def __init__(self, browser):
        self.browser = browser

    
    def safe_get_text(self, element, parent=None) -> str:
        """
        Safely extract text from a given web element.
        
        Parameters:
        - element: The web element from which text is to be extracted.

        Returns:
        - str: The extracted text.
        """

        try:
            return self.browser.find_element(element, parent=parent).text
        except:
            return ''

    
    def safe_get_image_url(self, element, parent=None) -> str:
        """
        Safely extract the image URL from a given web element.
        
        Parameters:
        - element: The web element from which the image URL is to be extracted.

        Returns:
        - str: The extracted image URL.
        """

        try:
            image_element = self.browser.find_element(element, parent=parent)
            return self.browser.get_element_attribute(image_element, "src")
        except:
            return ''
        

    
    def download_image_with_uuid(self, url: str, save_path: str) -> str:
        """
        Download an image from a given URL and save it with a unique filename.
        
        Parameters:
        - url: The URL of the image to be downloaded.
        - save_path: The directory where the image should be saved.

        Returns:
        - str: The path of the saved image file.
        """

        # Generate a unique filename using UUID
        filename = str(uuid.uuid4()) + ".jpg"
        filepath = os.path.join(save_path, filename)

        # Download the image
        if url:
            urllib.request.urlretrieve(url, filepath)
        else:
            return ''
        
        return filename

    
    def text_to_formatted_date(self, date_text: str) -> str:
        """
        Convert a text representation of a date to a formatted date string.
        
        Parameters:
        - date_text: The text representation of the date.

        Returns:
        - str: The formatted date string.
        """
        
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

    def calculate_search_dates_range(self, number_of_months) -> dict:
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

    
    def is_date_in_range(self, date: str, search_dates_range: dict) -> bool:
        """
        Check if a given date is within a specified date range.
        
        Parameters:
        - date: The date to check.
        - start_date: The start of the date range.
        - end_date: The end of the date range.

        Returns:
        - bool: True if the date is within the range, otherwise False.
        """
        start_date = datetime.datetime.strptime(search_dates_range['start_date'], '%m/%d/%Y')
        end_date = datetime.datetime.strptime(search_dates_range['end_date'], '%m/%d/%Y')
        current_date = datetime.datetime.strptime(date, '%m/%d/%Y')
        
        return start_date <= current_date <= end_date


    
    def contains_money_format_on_title_or_description(self, title: str, description: str) -> bool:
        """
        Check if the provided text contains any mention of money in specified formats.
        
        Parameters:
        - text: The text to check.

        Returns:
        - bool: True if money format is found, otherwise False.
        """
 
        # Define a regex pattern to match the specified money formats
        money_pattern = r"(\$[\d,]+(\.\d{1,2})?)|(\d+\s(dollars|USD))"
        
        # Search the pattern in the title and description
        if re.search(money_pattern, title) or re.search(money_pattern, description):
            return True
        return False

    
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
