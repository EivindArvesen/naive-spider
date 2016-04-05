# A Minimal Web Crawler
Naive, uses only the Python standard library.

Run the script with the command
```bash
python main.py
```

Can only deal with well formed documents, valid markup (with UTF-8 encoding).
No error handling on queries to SQLite.
If the crawler is interrupted while parsing, the program will behave as though
it finished parsing and extracting links from the URL in question.

Could probably do with support for rules (blacklist, etc.) and better model
abstraction (i.e. objects/classes for interactions with frontier and storage).

Were this a serious project I would probably base my work upon robust frameworks
like Scrapy and Beautiful Soup, to better handle scraping strategies and parsing
of broken markup, respectively.
