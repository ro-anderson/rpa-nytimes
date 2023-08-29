# New York Times Article Extractor 🤖 📰
This project automates the process of fetching articles from the New York Times website based on a search term, specific categories, and a date range. The data extracted includes the title, date, description, an associated image, and more. The results are then saved to an Excel file.

## Features

- **Article Extraction**: Extract articles' title, date, description, and associated image.
- **Date Range Filtering**: Filter articles based on a specified number of months.
- **Money Format Detection**: Detect mentions of money in specified formats within articles.
- **Search Phrase Count**: Count the number of times the search phrase appears in the articles.
- **Excel Export**: Export the extracted data to an Excel file.

### Disclaimer
As of the current date [```08/29/2023```], the date range search functionality on The New York Times website is not working as expected. When utilizing the filter for specific dates, all articles remain visible even after applying the filter. An example of this behavior can be observed at the following link:
- https://www.nytimes.com/search?dropmab=false&endDate=2000-12-31&query=brazil&startDate=1998-12-31 
  - try to filter a specific date range but returns the newest news related to the search phrase.

To address this issue, we have implemented methods in our automation to manually filter the articles based on the desired date range. However, it's worth noting that this solution is not as performant as if the native filtering on the site was functioning correctly.


## Requirements

- Python 3.7+
- Robocorp VSCode extension (for local development)
- Robocorp Workstation (for production deployment)

## Setup

1. **Local Development**:
    - Install [Robocorp's VSCode extension](https://robocorp.com/docs/development-guide/visual-studio-code-extension).
    - Clone this repository.
    - Open the project folder in VSCode.
    - Use the Robocorp VSCode extension to run and debug the automation.

2. **Production Deployment**:
    - Upload the project to Robocorp Workstation.
    - Use Robocorp Workstation's interface to start the automation.

## Usage

1. **Local Development**:
    - Open the `tasks.py` file in VSCode.
    - Use the Robocorp VSCode extension's play button to start the automation.

2. **Production Deployment**:
    - Navigate to the uploaded project within Robocorp Workstation.
    - Start the automation.

Sure! I'll update the "Important Notes" section to reflect the information you provided regarding setting variables through the `work-items.json` file.

---

## Important Notes

Ensure that the `search_phrase`, `news_categories`, and `number_of_months` are properly set for the automation. These variables can be adjusted in the `work-items.json` file located at:

```
devdata
├── work-items-in
│   └── work-items
│       └── work-items.json
```

The format of the `work-items.json` file should be:

```json
[
    {
        "payload": {
            "search_phrase": "YOUR_SEARCH_TERM",
            "news_categories": ["YOUR_CATEGORIES"],
            "number_of_months": YOUR_NUMBER_OF_MONTHS
        },
        "files": {}
    }
]

```
Replace `YOUR_SEARCH_TERM`, `YOUR_CATEGORIES`, and `YOUR_NUMBER_OF_MONTHS` with the desired values for your automation.

- `YOUR_SEARCH_TERM`: A string representing the term you want to search for. It can be any valid string or an empty string (`''`).
  
- `YOUR_CATEGORIES`: A list of categories that exist for the search term on the NYTimes search page. For example: `["Any", "Arts", "Briefing", "Business", "Magazine"]`. It can also be an empty list (`[]`).

- `YOUR_NUMBER_OF_MONTHS`: A positive integer representing the number of months for which you want to fetch articles. 
