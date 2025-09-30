
import requests

class ApiClient:
    """
    A class to interact with a REST API.
    """
    def __init__(self, base_url):
        """
        Initializes the API client.

        :param base_url: The base URL of the API.
        """
        self.base_url = base_url

    def get_data(self, endpoint):
        """
        Gets data from a specific API endpoint.

        :param endpoint: The API endpoint to get data from.
        :return: The data in JSON format if the request is successful, None otherwise.
        """
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url)
            response.raise_for_status()  # Raises an exception for error status codes (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None

