from typing import Dict

from gptchain.playground.provider import BaseProvider
from gptchain.playground.providers import (
    Anthropic,
    AzureChatOpenAI,
    AzureOpenAI,
    ChatOpenAI,
    OpenAI,
    ChatVertexAI,
    GenerationVertexAI,
)

providers = {
    AzureChatOpenAI.id: AzureChatOpenAI,
    AzureOpenAI.id: AzureOpenAI,
    ChatOpenAI.id: ChatOpenAI,
    OpenAI.id: OpenAI,
    Anthropic.id: Anthropic,
    ChatVertexAI.id: ChatVertexAI,
    GenerationVertexAI.id: GenerationVertexAI,
}  # type: Dict[str, BaseProvider]


def has_llm_provider(id: str):
    return id in providers


def add_llm_provider(provider: BaseProvider):
    if not provider.is_configured():
        raise ValueError(
            f"{provider.name} LLM provider requires the following environment variables: {', '.join(provider.env_vars.values())}"
        )
    providers[provider.id] = provider


def get_llm_providers():
    return [provider for provider in providers.values() if provider.is_configured()]
