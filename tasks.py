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

    return input_wi["search_phrase"]

def create_excel():


    # Create modern format workbook with a path set.
    excel_lib.create_workbook(path="./output/test.xlsx", fmt="xlsx")

    # Append an existing Table object
    table = {
        "name": ["Sara", "Beth", "Amy"],
        "age":  [    48,     21,     57],
        }
    
    excel_lib.append_rows_to_worksheet(table, header=True)

    excel_lib.save_workbook()
    

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
        create_excel()
        wi.add_work_item_file("./output/test.xlsx")
        wi.save_work_item()
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()