# bangalore-flat-and-flatmates-crawler

A crawler to fetch and store housing rent data from various groups on Facebook

## How to set up the Crawler

### Prerequisites

- Clone the repository
- Create a local/remote database and obtain the credentials/URL
- Create the following `.env` file in the root directory of the project

    ```bash
    DATABASE_URL="<your_database_url>"
    ```
    - The database URL should be a valid local or a remote database URL. If you intend to use the Docker deployment and use the database container, the database URL should be: `postgresql://postgres:postgres@postgres:5432/postgres`
- Install Docker and Docker Compose (if using Docker deployment)
- [Customize the Crawler](#customizing-the-crawler) to suit your needs

### Using Docker-Compose

The easiest way to set up the app is to use Docker-Compose. All you need to do is set up the `.env` (remember to set the database URL accordingly as mentioned in the prerequisites) - the `Dockerfile` and `docker-compose.yml` files will handle the rest. Run the following command to deploy the app:

```bash
cd docker/
docker-compose --project-name facebook-group-crawler up -d
 ```

### Using a Python Virtual Environment

If you want to use a Python virtual environment, you can do so by following the steps below:

- Create a virtual environment and install the requirements
    - `conda`
        ```bash
        conda create -n blr-housing python=3.9
        conda activate blr-housing
        pip install -r requirements.txt
        ```

    - `virtualenv`   
        ```bash
        virtualenv blr-housing
        source venv/bin/blr-housing
        pip install -r requirements.txt
        ```
- Run the following command to start the crawler
    ```bash
    python app/app.py
    ```

### Finding relevant results from Database

You can obtain the scraped results by accessing the database and running any of the following queries:
```sql
-- To get posts that match the keywords and filters
select * from post where keywords != '' and filters=true; 

-- To get posts that match a keyword
select * from post where keyword like '%old airport road%';

-- To get posts made in the last 1 hour
select * from post where time > now() - interval '1 hour';

-- To get posts where listed price is less than 20k
select * from post where listing_price < 20000;

```

You can set up another script that accesses the database and performs these queries periodically and connect it with a notification service that can inform you if anything relevant is found. Simple notification services can be email, telegram, discord bots, etc.

## Customizing the Crawler

The crawler is customizable to suit your needs and its behavior can be modified by changing the parameters in `conf/search_config.json`. The following parameters can be modified:

| Field           	| DataType        	| Description                                                                                                                                  	|
|-----------------	|-----------------	|----------------------------------------------------------------------------------------------------------------------------------------------	|
| `groups`          	| `list[str]`       	| A list of Facebook group IDs to search                                                                                                       	|
| `fields`          	| `list[str]`       	| A key:value map storing a post's field name and corresponding column name in the database                                                    	|
| `keywords`        	| `list[str]`      	| A list of key words/phrases that are searched for inside each post. Matched keywords are extracted and stored for each post                  	|
| `filters`         	| `list[str]`      	| A list of filter words/phrases that must be present in each post. If any filter is matched, the corresponding post is tagged in the database 	|
| `crawler_options` 	| `dict[str, bool]` 	| A key:value map storing options for the crawler                                                                                              	|
| `pages`           	| `int`             	| The number of pages to crawl per search                                                                                                      	|
| `interval`        	| `int`             	| The time interval in minutes to perform each search                                                                                          	|
| `spelling`        	| `int`             	| The degree of variation allowed in spellings while looking for keywords                                                                      	|

### More Information

- `groups`
    - Each Facebook group is crawled one after the other
    - The order of the groups in the list is the order in which the groups are fetched.
-  `fields`
    - You can customize which fields of a post are extracted and stored in the database
    - Each entry is of the form `post_property: database_column`. You can find all the properties in `conf/post_fields.json`
    - To add/remove a field, perform the following steps:
        - Make suitable changes to `conf/ddl.sql` to create the right schema for the database
        - Add/remove the fields from the `fields` list 
        - Ensure the database column names in the `fields` list matches the columns in the database in `ddl.sql`
- `keywords`
    - Words or phrases
    - Case-insensitive
    - Minor variations of the words are handled (for example, `"indiranagar"` and `"indranagar"` are treated as the same word)
    - If any of the keywords are matched, it is added to the list of keywords for that post in the database.
- `filters`
    - Words or phrases
    - Case-insensitive
    - Minor variations of the words are **NOT** handled (for example, `"indiranagar"` and `"indranagar"` are treated as different words here)
    - If any filter is matched, the corresponding post is tagged in the database.
    - Remember to be careful with filters, since they are matched as is (for example, using the filter `"male only"` will also match `"female only"` flats. You can tackle this by adding a whitespace before - `" male only"`)
- `crawler_options`
    - You can choose to fetch comments, reactions as well as make extra requests
    - By default, these are set to `False`. Setting any of them to `True` would result in making additional HTTP calls to fetch the corresponding fields and hence slow down the crawler
- `pages`
    - A smaller number of pages means a faster crawl of each group
    - Usually fetches about 10-20 posts per page and covers more than an hour's worth of posts
- `interval`
    - The interval in minutes the crawler is going to run
    - Do not set a low value here since it might lead to an IP ban for making too many successive requests
- `spelling`
    - The threshold applied to edit distance while finding variations in spelling of keywords
    - A higher value means that more variations will be considered when looking for keywords, and a lower value means fewer variations are considered
    - Increasing the value too much will result in false positives (for example, `"indiranagar"` might match with `"ramnagar"`)

## Why crawl Facebook groups?

Searching for flats and/or flatmates is a very daunting and tiresome task, especially when you move to a new city and there is a constant demand for good places to stay. A few Facebook (yes, the same social media platform we all ditched a few years ago) groups have been created to help people find flats and/or flatmates. Unfortunately, there are multiple posts in each group and there are over 20 groups. It is not feasible time-wise to look at each post on each group and check if it is relevant to your needs. Using the Facebook API requires admin access to these groups, which most of us don't have.

This project aims to crawl these groups and store the data in a database for easy access. It also comes with filters and keyword matching to help label the data that is fetched. This thus speeds up the process of finding a flat and/or flatmate.

### TLDR

This application is useful to you if:
- You are looking for a flat/flatmate in Bangalore
- You do not have time and/or energy to look at each post on each group
- You would prefer to only look at relevant listings and save time
- You do not have access to the Facebook API

## Extending this Crawler to other Facebook Groups

This project is a specific use-case to fetch data from Bangalore-based Facebook groups for searching flats/flatmates. It is not a generic crawler, but can be converted to one easily by changing the following:

- Change the `search_config.json` to include the groups you want to crawl
- Change the `filters` and `keywords` fields in `search_config.json` to include your filters and keywords

## Disclaimer

Facebook can detect unusual activity from your IP address if this application is overused. It might ban your IP address and restrict certain features of your account (for example, likes, comments, etc.) for some time. 

To ensure that this does not happen, please use this application responsibly. I recommend that you fetch posts once every 20 minutes only. I do not claim any responsibility for any harm done due to this application.