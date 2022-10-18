# bangalore-flat-and-flatmates-crawler

A crawler to fetch and store housing rent data from various groups on Facebook

## How to set up the Crawler

### Prerequisites

- Clone the repository
- Create a local/remote database and obtain the credentials/URL
- Create the following `.env` file in the root directory of the project

    ```bash
    DATABASE_URL="<your_database_url>"
    FACEBOOK_USERNAME="<your_facebook_email_or_password>"
    FACEBOOK_PASSWORD="<your_facebook_password>"
    ```
    - The database URL should be a valid local or a remote database URL. If you intend to use the Docker deployment and use the database container, the database URL should be: `postgresql://postgres:postgres@postgres:5432/postgres`
- Install Google Chrome and Chromedriver (if using Python virtual environment)
    - Download Chromedriver for your version (you can view this in Chrome settings) of Google Chrome from [here](https://chromedriver.chromium.org/downloads) and place it in the root directory of the project
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
select * from post where created_at > now() - interval '1 hour';

```

## Customizing the Crawler

The crawler is customizable to suit your needs and its behavior can be modified by changing the parameters in `conf/search_config.json`. The following parameters can be modified:

| Field    	| DataType  	| Description                                                                                                                                  	|
|----------	|-----------	|----------------------------------------------------------------------------------------------------------------------------------------------	|
| `groups`   	| `list[str]`	| A list of Facebook group IDs to search                                                                                                       	|
| `keywords` 	| `list[str]` 	| A list of key words/phrases that are searched for inside each post. Matched keywords are extracted and stored for each post.                   	|
| `filters`  	| `list[str]` 	| A list of filter words/phrases that must be exactly present in each post. If any filter is matched, the corresponding post is tagged in the database 	|

### More Information

- `groups`
    - Each Facebook group is crawled one after the other
    - The order of the groups in the list is the order in which the groups are fetched.
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

Facebook can detect unusual activity from your account if this application is overused. It might log you out from all your devices and restrict certain features of your account (for example: like, comments, etc.) for some time. 

To ensure that this does not happen, please use this application responsibly. I recommend that you fetch posts once every 20 minutes only. I do not claim any responsibility for any harm done due to this application.