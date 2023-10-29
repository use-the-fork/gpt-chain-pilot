from contextlib import contextmanager

from gptchain.input_widget import Select, Slider, Tags
from gptchain.playground.provider import BaseProvider
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

openai_common_inputs = [
    Slider(
        id="temperature",
        label="Temperature",
        min=0.0,
        max=2.0,
        step=0.01,
        initial=0.9,
        tooltip="Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.",
    ),
    Slider(
        id="max_tokens",
        label="Max Tokens",
        min=0.0,
        max=8000,
        step=1,
        initial=256,
        tooltip="The maximum number of tokens to generate in the chat completion.",
    ),
    Slider(
        id="top_p",
        label="Top P",
        min=0.0,
        max=1.0,
        step=0.01,
        initial=1.0,
        tooltip="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.",
    ),
    Slider(
        id="frequency_penalty",
        label="Frequency Penalty",
        min=-2.0,
        max=2.0,
        step=0.01,
        initial=0.0,
        tooltip="Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
    ),
    Slider(
        id="presence_penalty",
        label="Presence Penalty",
        min=-2.0,
        max=2.0,
        step=0.01,
        initial=0.0,
        tooltip="Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
    ),
    Tags(
        id="stop",
        label="Stop Sequences",
        initial=[],
        tooltip="Up to 4 sequences where the API will stop generating further tokens.",
    ),
]


@contextmanager
def handle_openai_error():
    import openai

    try:
        yield
    except openai.error.Timeout as e:
        raise HTTPException(
            status_code=408,
            detail=f"OpenAI API request timed out: {e}",
        )
    except openai.error.APIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API returned an API Error: {e}",
        )
    except openai.error.APIConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"OpenAI API request failed to connect: {e}",
        )
    except openai.error.InvalidRequestError as e:
        raise HTTPException(
            status_code=400,
            detail=f"OpenAI API request was invalid: {e}",
        )
    except openai.error.AuthenticationError as e:
        raise HTTPException(
            status_code=403,
            detail=f"OpenAI API request was not authorized: {e}",
        )
    except openai.error.PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=f"OpenAI API request was not permitted: {e}",
        )
    except openai.error.RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail=f"OpenAI API request exceeded rate limit: {e}",
        )


class ChatOpenAIProvider(BaseProvider):
    def format_message(self, message, prompt):
        message = super().format_message(message, prompt)
        return message.to_openai()

    async def create_completion(self, request):
        await super().create_completion(request)
        import openai

        env_settings = self.validate_env(request=request)

        deployment_id = self.get_var(request, "OPENAI_API_DEPLOYMENT_ID")

        if deployment_id:
            env_settings["deployment_id"] = deployment_id

        llm_settings = request.prompt.settings

        self.require_settings(llm_settings)

        messages = self.create_prompt(request)

        if "stop" in llm_settings:
            stop = llm_settings["stop"]

            # OpenAI doesn't support an empty stop array, clear it
            if isinstance(stop, list) and len(stop) == 0:
                stop = None

            llm_settings["stop"] = stop

        llm_settings["stream"] = True

        with handle_openai_error():
            response = await openai.ChatCompletion.acreate(
                **env_settings,
                messages=messages,
                **llm_settings,
            )

        async def create_event_stream():
            async for stream_resp in response:
                if hasattr(stream_resp, 'choices') and len(stream_resp.choices) > 0:
                    token = stream_resp.choices[0]["delta"].get("content", "")
                    yield token
                else:
                    continue

        return StreamingResponse(create_event_stream())


class OpenAIProvider(BaseProvider):
    def message_to_string(self, message):
        return message.to_string()

    async def create_completion(self, request):
        await super().create_completion(request)
        import openai

        env_settings = self.validate_env(request=request)

        deployment_id = self.get_var(request, "OPENAI_API_DEPLOYMENT_ID")

        if deployment_id:
            env_settings["deployment_id"] = deployment_id

        llm_settings = request.prompt.settings

        self.require_settings(llm_settings)

        prompt = self.create_prompt(request)

        if "stop" in llm_settings:
            stop = llm_settings["stop"]

            # OpenAI doesn't support an empty stop array, clear it
            if isinstance(stop, list) and len(stop) == 0:
                stop = None

            llm_settings["stop"] = stop

        llm_settings["stream"] = True

        with handle_openai_error():
            response = await openai.Completion.acreate(
                **env_settings,
                prompt=prompt,
                **llm_settings,
            )

        async def create_event_stream():
            async for stream_resp in response:
                token = stream_resp.get("choices")[0].get("text")
                yield token

        return StreamingResponse(create_event_stream())


openai_env_vars = {"api_key": "OPENAI_API_KEY"}

azure_openai_env_vars = {
    "api_key": "OPENAI_API_KEY",
    "api_type": "OPENAI_API_TYPE",
    "api_base": "OPENAI_API_BASE",
    "api_version": "OPENAI_API_VERSION",
}

ChatOpenAI = ChatOpenAIProvider(
    id="openai-chat",
    env_vars=openai_env_vars,
    name="ChatOpenAI",
    inputs=[
        Select(
            id="model",
            label="Model",
            values=["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4", "gpt-4-32k"],
            initial_value="gpt-3.5-turbo",
        ),
        *openai_common_inputs,
    ],
    is_chat=True,
)


AzureChatOpenAI = ChatOpenAIProvider(
    id="azure-openai-chat",
    env_vars=azure_openai_env_vars,
    name="AzureChatOpenAI",
    inputs=openai_common_inputs,
    is_chat=True,
)

OpenAI = OpenAIProvider(
    id="openai",
    name="OpenAI",
    env_vars=openai_env_vars,
    inputs=[
        Select(
            id="model",
            label="Model",
            values=["text-davinci-003", "text-davinci-002"],
            initial_value="text-davinci-003",
        ),
        *openai_common_inputs,
    ],
    is_chat=False,
)

AzureOpenAI = OpenAIProvider(
    id="azure",
    name="AzureOpenAI",
    env_vars=azure_openai_env_vars,
    inputs=openai_common_inputs,
    is_chat=False,
)
