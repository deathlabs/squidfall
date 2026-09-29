# Standard library imports.
from langchain_core.language_models.base import BaseLanguageModel

# Local imports.
from .openai import get_openai_model, get_openai_model_from_azure


def get_model_client(model_provider: str) -> BaseLanguageModel:
    """Fetches a model client based on the model provider given."""
    match model_provider:
        case "openai":
            return get_openai_model()
        case "azure_openai":
            return get_openai_model_from_azure()
        case _:
            raise ValueError("Invalid MODEL_PROVIDER. Options: openai or azure_openai.")
