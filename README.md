# A Minimal Web Crawler
A naive implementation of a spider that depends only on the Python standard library.
It is able to resume operations if shut down (via ctrl+c).

Run the script with the command
```bash
python main.py <URL(s) to start with>
```

The applications takes an arbitrary number of URLs to start with as arguments.
It then saves urls to a queue and to a database.
Then, if there is a document at the URL, it downloads this to a databse, parses it and finds any links, and adds these to the queue.
This work is preformed on several threads concurrently.

## Assumptions
This crawler assumes that Python (2.x.x) is available, and that there is a functional SQLite installation.

## Limitations
The program can only deal with well formed documents - valid markup (with UTF-8 encoding).

Were this a serious project I would probably base my work upon robust frameworks
like Scrapy and Beautiful Soup, to better handle scraping strategies and parsing
of broken markup, respectively.

## Possible future improvements
- Error handling on queries to SQLite.
- Not behaving as though the crawler is finished parsing and extracting links from current URL if it is interrupted while parsing.
- Serialization/saving should be optimized.
- Separate the tasks of downloading and saving document, and parsing document to find links into different processes.
- Add rule support (blacklisting, etc.)
- Better model abstraction (i.e. objects/classes for interactions with frontier and storage).
- Reorganization of some code, e.g. dealing with args etc. elsewhere.
