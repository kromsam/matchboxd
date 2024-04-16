import requests


def update_api_url_pagecount(api_response):
    # Make the initial request to get the count and TotalCount
    initial_response = requests.get(api_url)
    initial_data = initial_response.json()

    count = initial_data.get("count")
    total_count = initial_data.get("totalCount")

    # Check if TotalCount is higher than the current count
    if total_count > count:
        # Update the page limit to retrieve all results in a single page
        api_url = f"{api_url}&page[limit]={total_count}"
    return api_url
