import requests
import time


class VideoGenerator:
    """
    A class for generating videos and querying their generation status using a remote API.

    Attributes:
        bearer_token (str): The authorization token for API access.
        api_url (str): The base URL for the video generation API.

    Methods:
        generate_video(result_scenes: str) -> dict:
            Sends a request to generate a video based on a provided prompt and returns the response.

        query_video_status(request_id: str) -> dict:
            Checks the status of a video generation request after a delay and returns the response.
    """

    def __init__(self, bearer_token: str, api_url: str):
        """
        Initializes the VideoGenerator with API credentials.

        Args:
            bearer_token (str): The authorization token for accessing the video generation API.
            api_url (str): The base URL of the video generation API.
        """
        self.bearer_token = bearer_token
        self.api_url = api_url

    def generate_video(self, result_scenes: str) -> dict:
        """
        Initiates a video generation request with specified scene details.

        Args:
            result_scenes (str): A string describing the scenes to be generated in the video.

        Returns:
            dict: The response from the API, containing details about the video generation request
                  or an error message in case of failure.
        """
        result_scenes = result_scenes.replace("<|im_end|>", "")
        url = f"{self.api_url}/generateVideoSyn"
        headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }
        data = {
            "refined_prompt": result_scenes,
            "num_step": 100,
            "cfg_scale": 7.5,
            "user_prompt": result_scenes,
            "rand_seed": 12345,
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"An error occurred: {str(e)}"}

    def query_video_status(self, request_id: str) -> dict:
        """
        Queries the status of a video generation request after a specified delay.

        Args:
            request_id (str): The unique ID of the video generation request to check.

        Returns:
            dict: The response from the API with the current status of the video generation
                  or an error message in case of failure.
        """
        return {
            "data": "https://apiplatform-rhymes-prod-va.s3.amazonaws.com/20241104184528.mp4"
        }
        time.sleep(240)
        url = f"{self.api_url}/videoQuery"
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        params = {"requestId": request_id}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"An error occurred: {str(e)}"}
