import textwrap
from typing import TypedDict, List, Optional

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam, ChatCompletionSystemMessageParam

TOOL_PROMPT = textwrap.dedent(
    """
    You will be given a list of tools and the ID of each tool. Based on the provided prompt, pick a tool by replying with JUST its ID.
    The tool you pick should be whichever one is most relevant to answering the prompt.
    
    For example, if you received the prompt:
    
    PROMPT: Send pics please
    TOOLS:
        1. Send a picture
        2. Send a text message response
        3. Send an album
        4. ...
    
    You should reply: 1
    
    Now it's your turn:        
    
    PROMPT: %s
    TOOLS:
    %s
    
    Your response:
    """
)

Message = ChatCompletionMessageParam
Chat = List[Message]


class Tool(TypedDict):
    id: int
    description: str
    fn_code: Optional[str]


def create_chat(
        prompt: str,
        tools: List[Tool]
) -> Chat:
    tool_format: str = "\n".join([f"    {tool['id']}. {tool['description']}" for tool in tools])

    return [
        ChatCompletionSystemMessageParam(
            role="system",
            content=TOOL_PROMPT % (prompt, tool_format)
        )
    ]


async def pick_tool(
        prompt: str,
        tools: List[Tool],
        llm: AsyncOpenAI
) -> Optional[str]:
    text_gen: ChatCompletion = await llm.chat.completions.create(
        model="gpt-4o",
        messages=create_chat(prompt, tools),
        max_tokens=1,
        temperature=0.1
    )

    try:
        tool_choice = int(text_gen.choices[0].message.content.strip())
        return tools[tool_choice - 1]["fn_code"]
    except ValueError:
        return None
