# Property Search Program

This Python-based program searches for properties on the [Homegate](https://www.homegate.ch/) website, a Swiss real estate portal, based on user-defined search criteria.

## Functionality

The program parses a list of postcodes and distances from a user-specified JSON configuration file, and uses these to generate URLs for property searches. It then scrapes the content of these URLs to extract property links.

The program identifies the total number of result pages for each postcode-distance combination and generates URLs for all these pages.

For each property link, the program checks whether the property page contains any user-specified search terms (also defined in the JSON configuration file). If a search term is present, the property link is considered a possible match; otherwise, it's considered a rejected match.

All possible and rejected matches are saved to separate JSON files.

The program also has email functionality. It sends an email containing a list of all new possible matches, as well as all previously found matches, to a user-specified email address.

## Usage

1. Make sure Python 3.8 or later is installed on your system.
2. Install the required Python libraries (requests, BeautifulSoup4, and smtplib) if you haven't done so already.
3. Configure your search parameters in a JSON configuration file. The file should be structured as follows:

```json
{
  "url_template": "https://www.homegate.ch/mieten/wohnung/plz-{postcode}/trefferliste?ep={page}&be={distance}",
  "postcodes": [
    "8001",
    "8002"
  ],
  "distances": [
    "1000",
    "2000"
  ],
  "search_terms": [
    "garage",
    "parkplatz"
  ],
  "possible_file": "possible.json",
  "rejected_file": "rejected.json",
  "search_name": "My Property Search",
}
```

4. Configure your email settings in a JSON configuration file. The file should be structured as follows:
```json
{
  "email_recipient": "your-email@example.com",
  "smtp_server": "your-smtp-server",
  "smtp_port": 587, #probably
  "smtp_username": "your-smtp-username",
  "smtp_password": "your-smtp-password"
}
```