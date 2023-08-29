from RPA.Excel.Files import Files

class ExcelHandler:
    """Handles Excel operations."""

    def __init__(self):
        self.excel_file = Files()

    def create_excel(self, list_articles: list, output_path="./output/articles.xlsx"):
        """
        Create an Excel file with the provided list of articles.
        
        Args:
        - list_articles (list): List of article dictionaries to be written to the Excel file.
        - output_path (str): Path where the Excel file will be saved.
        
        Returns:
        - None
        """
        # Create modern format workbook with a path set.
        self.excel_file.create_workbook(path=output_path, fmt="xlsx")

        # Append an existing Table object
        table = self.transform_article_data(list_articles)
        
        self.excel_file.append_rows_to_worksheet(table, header=True)
        self.excel_file.save_workbook(output_path)

    @staticmethod
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
