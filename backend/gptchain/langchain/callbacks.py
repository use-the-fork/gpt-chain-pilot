import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from gptchain.context import context_var
from gptchain.message import Message
from gptchain.prompt import Prompt, PromptMessage
from langchain.callbacks.tracers.base import BaseTracer
from langchain.callbacks.tracers.schemas import Run
from langchain.schema.messages import BaseMessage
from langchain.schema.output import ChatGenerationChunk, GenerationChunk

DEFAULT_ANSWER_PREFIX_TOKENS = ["Final", "Answer", ":"]


class FinalStreamHelper:
    # The stream we can use to stream the final answer from a chain
    final_stream: Union[Message, None]
    # Should we stream the final answer?
    stream_final_answer: bool = False
    # Token sequence that prefixes the answer
    answer_prefix_tokens: List[str]
    # Ignore white spaces and new lines when comparing answer_prefix_tokens to last tokens? (to determine if answer has been reached)
    strip_tokens: bool

    answer_reached: bool

    def __init__(
        self,
        answer_prefix_tokens: Optional[List[str]] = None,
        stream_final_answer: bool = False,
        force_stream_final_answer: bool = False,
        strip_tokens: bool = True,
    ) -> None:
        # Langchain final answer streaming logic
        if answer_prefix_tokens is None:
            self.answer_prefix_tokens = DEFAULT_ANSWER_PREFIX_TOKENS
        else:
            self.answer_prefix_tokens = answer_prefix_tokens
        if strip_tokens:
            self.answer_prefix_tokens_stripped = [
                token.strip() for token in self.answer_prefix_tokens
            ]
        else:
            self.answer_prefix_tokens_stripped = self.answer_prefix_tokens

        self.last_tokens = [""] * len(self.answer_prefix_tokens)
        self.last_tokens_stripped = [""] * len(self.answer_prefix_tokens)
        self.strip_tokens = strip_tokens
        self.answer_reached = force_stream_final_answer

        # Our own final answer streaming logic
        self.stream_final_answer = stream_final_answer
        self.final_stream = None
        self.has_streamed_final_answer = False

    def _check_if_answer_reached(self) -> bool:
        if self.strip_tokens:
            return self._compare_last_tokens(self.last_tokens_stripped)
        else:
            return self._compare_last_tokens(self.last_tokens)

    def _compare_last_tokens(self, last_tokens: List[str]):
        if last_tokens == self.answer_prefix_tokens_stripped:
            # If tokens match perfectly we are done
            return True
        else:
            # Some LLMs will consider all the tokens of the final answer as one token
            # so we check if any last token contains all answer tokens
            return any(
                [
                    all(
                        answer_token in last_token
                        for answer_token in self.answer_prefix_tokens_stripped
                    )
                    for last_token in last_tokens
                ]
            )

    def _append_to_last_tokens(self, token: str) -> None:
        self.last_tokens.append(token)
        self.last_tokens_stripped.append(token.strip())
        if len(self.last_tokens) > len(self.answer_prefix_tokens):
            self.last_tokens.pop(0)
            self.last_tokens_stripped.pop(0)


class PromptHelper:
    prompt_sequence: List[Prompt]

    def __init__(self) -> None:
        self.prompt_sequence = []

    @property
    def current_prompt(self):
        return self.prompt_sequence[-1] if self.prompt_sequence else None

    def _convert_message_role(self, role: str):
        if "human" in role.lower():
            return "user"
        elif "system" in role.lower():
            return "system"
        elif "function" in role.lower():
            return "function"
        else:
            return "assistant"

    def _convert_message_dict(
        self,
        message: Dict,
        template: Optional[str] = None,
        template_format: Optional[str] = None,
    ):
        class_name = message["id"][-1]
        kwargs = message.get("kwargs", {})
        function_call = kwargs.get("additional_kwargs", {}).get("function_call")
        if function_call:
            content = json.dumps(function_call, indent=4)
        else:
            content = kwargs.get("content", "")
        return PromptMessage(
            name=kwargs.get("name"),
            role=self._convert_message_role(class_name),
            template=template,
            template_format=template_format,
            formatted=content,
        )

    def _convert_message(
        self,
        message: Union[Dict, BaseMessage],
        template: Optional[str] = None,
        template_format: Optional[str] = None,
    ):
        if isinstance(message, dict):
            return self._convert_message_dict(
                message,
            )
        function_call = message.additional_kwargs.get("function_call")
        if function_call:
            content = json.dumps(function_call, indent=4)
        else:
            content = message.content
        return PromptMessage(
            name=getattr(message, "name", None),
            role=self._convert_message_role(message.type),
            template=template,
            template_format=template_format,
            formatted=content,
        )

    def _get_messages(self, serialized: Dict):
        # In LCEL prompts messages are not at the same place
        lcel_messages = serialized.get("kwargs", {}).get(
            "messages", []
        )  # type: List[Dict]
        if lcel_messages:
            return lcel_messages
        else:
            # For chains
            prompt_params = (
                serialized.get("kwargs", {}).get("prompt", {}).get("kwargs", {})
            )
            chain_messages = prompt_params.get("messages", [])  # type: List[Dict]

            return chain_messages

    def _build_prompt(self, serialized: Dict, inputs: Dict):
        messages = self._get_messages(serialized)
        if messages:
            # If prompt is chat, the formatted values will be added in on_chat_model_start
            self._build_chat_template_prompt(messages, inputs)
        else:
            # For completion prompt everything is done here
            self._build_completion_prompt(serialized, inputs)

    def _build_completion_prompt(self, serialized: Dict, inputs: Dict):
        if not serialized:
            return
        kwargs = serialized.get("kwargs", {})
        template = kwargs.get("template")
        template_format = kwargs.get("template_format")
        stringified_inputs = {k: str(v) for (k, v) in inputs.items()}

        self.prompt_sequence.append(
            Prompt(
                template=template,
                template_format=template_format,
                inputs=stringified_inputs,
            )
        )

    def _build_default_prompt(
        self,
        run: Run,
        generation_type: str,
        provider: str,
        llm_settings: Dict,
        completion: str,
    ):
        """Build a prompt once an LLM has been executed if no current prompt exists (without template)"""
        if "chat" in generation_type.lower():
            return Prompt(
                provider=provider,
                settings=llm_settings,
                completion=completion,
                messages=[
                    PromptMessage(
                        formatted=formatted_prompt,
                        role=self._convert_message_role(formatted_prompt.split(":")[0]),
                    )
                    for formatted_prompt in run.inputs.get("prompts", [])
                ],
            )
        else:
            return Prompt(
                provider=provider,
                settings=llm_settings,
                completion=completion,
                formatted=run.inputs.get("prompts", [])[0],
            )

    def _build_chat_template_prompt(self, lc_messages: List[Dict], inputs: Dict):
        def build_template_messages() -> List[PromptMessage]:
            template_messages = []  # type: List[PromptMessage]

            if not lc_messages:
                return template_messages

            for lc_message in lc_messages:
                message_kwargs = lc_message.get("kwargs", {})
                class_name = lc_message["id"][-1]  # type: str
                prompt = message_kwargs.get("prompt", {})
                prompt_kwargs = prompt.get("kwargs", {})
                template = prompt_kwargs.get("template")
                template_format = prompt_kwargs.get("template_format")

                if "placeholder" in class_name.lower():
                    variable_name = lc_message.get(
                        "variable_name"
                    )  # type: Optional[str]
                    variable = inputs.get(variable_name, [])
                    placeholder_size = len(variable)
                    if placeholder_size:
                        template_messages += [
                            PromptMessage(placeholder_size=placeholder_size)
                        ]
                else:
                    template_messages += [
                        PromptMessage(
                            template=template,
                            template_format=template_format,
                            role=self._convert_message_role(class_name),
                        )
                    ]
            return template_messages

        template_messages = build_template_messages()

        stringified_inputs = {k: str(v) for (k, v) in inputs.items()}
        self.prompt_sequence.append(
            Prompt(messages=template_messages, inputs=stringified_inputs)
        )

    def _build_chat_formatted_prompt(
        self, lc_messages: Union[List[BaseMessage], List[dict]]
    ):
        if not self.current_prompt:
            return

        formatted_messages = []  # type: List[PromptMessage]
        if self.current_prompt.messages:
            # This is needed to compute the correct message index to read
            placeholder_offset = 0
            # The final list of messages
            formatted_messages = []
            # Looping the messages built in build_prompt
            # They only contain the template
            for template_index, template_message in enumerate(
                self.current_prompt.messages
            ):
                # If a message has a placeholder size, we need to replace it
                # With the N following messages, where N is the placeholder size
                if template_message.placeholder_size:
                    for _ in range(template_message.placeholder_size):
                        lc_message = lc_messages[template_index + placeholder_offset]
                        formatted_messages += [self._convert_message(lc_message)]
                        # Increment the placeholder offset
                        placeholder_offset += 1
                    # Finally, decrement the placeholder offset by one
                    # Because the message representing the placeholder is now consumed
                    placeholder_offset -= 1
                # The current message is not a placeholder
                else:
                    lc_message = lc_messages[template_index + placeholder_offset]
                    # Update the role and formatted value, keep the template
                    formatted_messages += [
                        self._convert_message(
                            lc_message,
                            template=template_message.template,
                            template_format=template_message.template_format,
                        )
                    ]
            # If the chat llm has more message than the initial chain prompt, append them
            # Typically happens with function agents
            if len(lc_messages) > len(formatted_messages):
                formatted_messages += [
                    self._convert_message(m)
                    for m in lc_messages[len(formatted_messages) :]
                ]
        else:
            formatted_messages = [
                self._convert_message(lc_message) for lc_message in lc_messages
            ]

        self.current_prompt.messages = formatted_messages

    def _build_llm_settings(
        self,
        serialized: Dict,
        invocation_params: Optional[Dict] = None,
    ):
        # invocation_params = run.extra.get("invocation_params")
        if invocation_params is None:
            return None, None

        provider = invocation_params.pop("_type", "")  # type: str

        model_kwargs = invocation_params.pop("model_kwargs", {})

        if model_kwargs is None:
            model_kwargs = {}

        merged = {
            **invocation_params,
            **model_kwargs,
            **serialized.get("kwargs", {}),
        }

        # make sure there is no api key specification
        settings = {k: v for k, v in merged.items() if not k.endswith("_api_key")}

        return provider, settings


class LangchainTracer(BaseTracer, PromptHelper, FinalStreamHelper):
    llm_stream_message: Dict[str, Message]

    def __init__(
        self,
        answer_prefix_tokens: Optional[List[str]] = None,
        stream_final_answer: bool = False,
        force_stream_final_answer: bool = False,
        **kwargs: Any,
    ) -> None:
        BaseTracer.__init__(self, **kwargs)
        PromptHelper.__init__(self)
        FinalStreamHelper.__init__(
            self,
            answer_prefix_tokens=answer_prefix_tokens,
            stream_final_answer=stream_final_answer,
            force_stream_final_answer=force_stream_final_answer,
        )
        self.context = context_var.get()
        self.llm_stream_message = {}

    def _run_sync(self, co):
        asyncio.run_coroutine_threadsafe(co, loop=self.context.loop)

    def _persist_run(self, run: Run) -> None:
        pass

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Adding formatted content and new message to the previously built template prompt"""
        lc_messages = messages[0]
        if not self.current_prompt:
            self.prompt_sequence.append(
                Prompt(messages=[self._convert_message(m) for m in lc_messages])
            )
        else:
            self._build_chat_formatted_prompt(lc_messages)

        super().on_chat_model_start(
            serialized,
            messages,
            run_id=run_id,
            parent_run_id=parent_run_id,
            tags=tags,
            metadata=metadata,
            **kwargs,
        )

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: Optional[Union[GenerationChunk, ChatGenerationChunk]] = None,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        msg = self.llm_stream_message.get(str(run_id), None)
        if msg:
            self._run_sync(msg.stream_token(token))

        if self.stream_final_answer:
            self._append_to_last_tokens(token)

            if self.answer_reached:
                if not self.final_stream:
                    self.final_stream = Message(content="")
                self._run_sync(self.final_stream.stream_token(token))
                self.has_streamed_final_answer = True
            else:
                self.answer_reached = self._check_if_answer_reached()

        BaseTracer.on_llm_new_token(
            self,
            token,
            chunk=chunk,
            run_id=run_id,
            parent_run_id=parent_run_id,
            **kwargs,
        )

    def _start_trace(self, run: Run) -> None:
        super()._start_trace(run)

        context_var.set(self.context)
        root_message_id = (
            self.context.session.root_message.id
            if self.context.session.root_message
            else None
        )
        parent_id = str(run.parent_run_id) if run.parent_run_id else root_message_id
        if run.run_type in ["chain", "prompt"]:
            # Prompt templates are contained in chains or prompts (lcel)
            self._build_prompt(run.serialized or {}, run.inputs)

        if run.run_type == "llm":
            msg = Message(
                id=run.id,
                content="",
                author=run.name,
                parent_id=parent_id,
            )
            self.llm_stream_message[str(run.id)] = msg
            self._run_sync(msg.send())
            return

        content = run.inputs

        self._run_sync(
            Message(
                id=run.id,
                content=content,
                language="json",
                author=run.name,
                parent_id=parent_id,
            ).send()
        )

    def _on_run_update(self, run: Run) -> None:
        """Process a run upon update."""
        context_var.set(self.context)

        root_message_id = (
            self.context.session.root_message.id
            if self.context.session.root_message
            else None
        )
        parent_id = str(run.parent_run_id) if run.parent_run_id else root_message_id

        if run.run_type in ["chain"]:
            if self.prompt_sequence:
                self.prompt_sequence.pop()

        if run.run_type == "llm":
            provider, llm_settings = self._build_llm_settings(
                (run.serialized or {}), (run.extra or {}).get("invocation_params")
            )
            generations = (run.outputs or {}).get("generations", [])
            completion = generations[0][0]["text"]
            generation_type = generations[0][0]["type"]

            current_prompt = (
                self.prompt_sequence.pop() if self.prompt_sequence else None
            )

            if current_prompt:
                current_prompt.provider = provider
                current_prompt.settings = llm_settings
                current_prompt.completion = completion
            else:
                current_prompt = self._build_default_prompt(
                    run, generation_type, provider, llm_settings, completion
                )
            msg = self.llm_stream_message.get(str(run.id), None)
            if msg:
                msg.content = completion
                msg.prompt = current_prompt
                self._run_sync(msg.update())
            return

        if run.run_type in ["agent", "chain", "tool"]:
            # Add the response of the chain/tool
            self._run_sync(
                Message(
                    content=run.outputs or {},
                    language="json",
                    author=run.name,
                    parent_id=parent_id,
                ).send()
            )
        else:
            self._run_sync(
                Message(
                    id=run.id,
                    content=run.outputs or {},
                    language="json",
                    author=run.name,
                    parent_id=parent_id,
                ).update()
            )


LangchainCallbackHandler = LangchainTracer
AsyncLangchainCallbackHandler = LangchainTracer
