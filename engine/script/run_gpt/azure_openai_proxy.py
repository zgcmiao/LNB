import os
# from openai import AzureOpenAI

DEFAULT_API_VERSION = "2023-09-01-preview"

class AzureOpenAIProxy:
    def __init__(self, _azure_endpoint, _api_version=DEFAULT_API_VERSION):
        self.client = None
        self.azure_api_key = ''
        self.api_version = _api_version
        self.azure_endpoint = _azure_endpoint

    def get_client(self):
        if not os.getenv('AZURE_OPENAI_API_KEY'):
            os.environ['AZURE_OPENAI_API_KEY'] = self.azure_api_key

        # gets the API Key from environment variable AZURE_OPENAI_API_KEY
        from openai import AzureOpenAI
        client = AzureOpenAI(
            # https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#rest-api-versioning
            api_version=self.api_version,
            # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
            azure_endpoint=self.azure_endpoint,
        )
        return client



