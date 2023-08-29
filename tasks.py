from src.nyt_pages import HomePage, SearchResultsPage
from RPA.Browser.Selenium import Selenium
browser = Selenium()

if __name__ == '__main__':

    home_page = HomePage(browser)
    home_page.open_the_website(home_page.url)
    search_results_page = SearchResultsPage(browser)
    search_results_page.apply_filters()
    search_results_page.extract_articles()

