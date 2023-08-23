from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems

browser_lib = Selenium()

def get_work_item_data():

    # Load the current work item
    wi = WorkItems()
    wi.get_input_work_item() 
    input_wi = wi.get_work_item_variables() 
    print(input_wi['search_phrase']) 
    print(input_wi['news_category'])
    print(input_wi['number_of_months'])

    return input_wi["search_phrase"]

def open_the_website(url):
    browser_lib.open_available_browser(url)


def search_for():
    term = get_work_item_data()
    input_field = "css:input"
    browser_lib.input_text(input_field, term)
    browser_lib.press_keys(input_field, "ENTER")


def store_screenshot(filename):
    browser_lib.screenshot(filename=filename)


# Define a main() function that calls the other functions in order:
def main():
    try:
        open_the_website("https://robocorp.com/docs/")
        search_for()
        store_screenshot("output/screenshot.png")
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()