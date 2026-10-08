from typing import Type, Any

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from app.agents.runtime.definition import AgentDefinition
from app.caching.prompt_cache import PromptCache
from app.schemas import cache


class AgentRuntime:
    """
        Generic runtime for Markdown-defined agents.

        Responsibilities:

        - receive an AgentDefinition
        - create the LLM
        - optionally bind tools
        - request structured output
        - validate the result
        - optionally use Redis prompt caching

        Workflow orchestration does NOT belong here.
        """

    def __init__(
            self,
            *,
            definition: AgentDefinition,
            output_schema: Type[BaseModel],
            model: str = "qwen3:8b",
            temperature: float = 0.0,
            tools: list[Any] | None = None,
            prompt_cache: PromptCache | None = None,
            enable_cache: bool = False,
    ):
        self.definition = definition
        self.output_schema = output_schema
        self.model = model
        self.temperature = temperature
        self.tools = tools or []
        self.prompt_cache = prompt_cache
        self.enable_cache = enable_cache

        self.llm = ChatOllama(
            model=self.model,
            temperature=self.temperature,
        )

        if self.tools:
            self.llm.bind_tools(self.tools)

        self.structured_llm = self.llm.with_structured_output(output_schema)

    async def run(self, *, user_input: str) -> BaseModel:
        cache_key = None

        if self.enable_cache and self.prompt_cache:
            cache_key = self._create_cache_key(user_input)
            cached = self.prompt_cache.get(cache_key)

            if cached:
                return self.output_schema.model_validate(cached["response"])

        messages = [
            SystemMessage(content=self.definition.system_prompt),
            HumanMessage(content=user_input),
        ]

        result = await self.structured_llm.ainvoke(
            messages
        )

        validated = self.output_schema.model_validate(
            result
        )

        if (
                self.enable_cache
                and self.prompt_cache
                and cache_key
        ):
            await self.prompt_cache.set(
                cache_key=cache_key,
                response=validated.model_dump(mode="json"),
                metadata={
                    "agent": self.definition.name,
                    "model": self.model,
                },
            )
        return validated

    def _create_cache_key(self, user_input: str) -> str:
        cache_key = cache.CacheKeyInput(
            model=self.model,
            system_prompt=self.definition.system_prompt,
            user_prompt=user_input,
            temperature=self.temperature,
        )

        return self.prompt_cache.create_cache_key(cache_key)
