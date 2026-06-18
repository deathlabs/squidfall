# Standard library imports.
from os import environ


def get_openai_model():
    # Third party imports.
    from langchain_openai import ChatOpenAI

    # Get environment variables.
    OPENAI_MODEL = environ["OPENAI_MODEL"]
    OPENAI_API_KEY = environ["OPENAI_API_KEY"]

    return ChatOpenAI(model=OPENAI_MODEL, api_key=OPENAI_API_KEY)


def get_openai_model_from_azure():
    # Third party imports.
    from azure.identity import (
        AzureAuthorityHosts,
        DefaultAzureCredential,
        get_bearer_token_provider,
    )
    from langchain_openai import AzureChatOpenAI

    # Get environment variables.
    AZURE_AUTHORITY_HOSTS = environ["AZURE_AUTHORITY_HOSTS"]
    AZURE_TOKEN_SCOPES = environ["AZURE_TOKEN_SCOPES"]
    AZURE_OPENAI_ENDPOINT = environ["AZURE_OPENAI_ENDPOINT"]
    AZURE_OPENAI_DEPLOYMENT = environ["AZURE_OPENAI_DEPLOYMENT"]
    AZURE_OPENAI_API_VERSION = environ["AZURE_OPENAI_API_VERSION"]

    # Authenticate with Azure.
    credential = DefaultAzureCredential(authority=AZURE_AUTHORITY_HOSTS)

    # Get an authorization token provider.
    token_provider = get_bearer_token_provider(
        credential,
        AZURE_TOKEN_SCOPES,
    )

    return AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_deployment=AZURE_OPENAI_DEPLOYMENT,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_ad_token_provider=token_provider,
    )
