import os
import asyncio
import datetime
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
import requests
import re


def bocha_search(query: str) -> str:
    """
    Performs a web search using Bocha SearchAPI.

    Args:
        query: The search query

    Returns:
        Formatted string summary of the search results
    """
    api_key = os.getenv("BOCHA_API_KEY")
    if not api_key:
        print("BOCHA_API_KEY is not set. Please obtain a key from https://open.bochaai.com and add it to your .env file.")
        exit(1)

    url = "https://api.bochaai.com/v1/ai/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        search_results = response.json()

        # Format the results
        formatted_results = []
        if "results" in search_results:
            for i, result in enumerate(search_results["results"], 1):
                title = result.get("title", "No title")
                url = result.get("url", "No URL")
                snippet = result.get("snippet", "No snippet")
                formatted_results.append(f"{i}. {title}\n   URL: {url}\n   Snippet: {snippet}\n")

        return "\n".join(formatted_results) if formatted_results else "No search results found."

    except requests.exceptions.RequestException as e:
        return f"Error performing search: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


class State(TypedDict):
    """
    Shared state for the multi-agent marketing system.
    """
    product: str                    # The product being marketed
    research_report: str           # Market research report
    strategy: str                  # Marketing strategy
    content: str                   # Created content pieces
    error: str                     # Error message if any


def create_llm(model: str, base_url: str, api_key_env: str):
    """
    Creates and returns a ChatOpenAI instance configured for the specified model.
    Exits if the API key is missing.

    Args:
        model: The model name to use
        base_url: The API base URL
        api_key_env: The environment variable name for the API key

    Returns:
        Configured ChatOpenAI instance
    """
    api_key = os.getenv(api_key_env)
    if not api_key:
        print(f"Error: {api_key_env} environment variable is not set.")
        print(f"Please set the {api_key_env} in your .env file.")
        exit(1)

    return ChatOpenAI(
        model=model,
        openai_api_base=base_url,
        openai_api_key=api_key,
        temperature=0.7
    )


async def market_research_node(state: State) -> dict:
    """
    Performs market research for the given product using GLM-4 Plus with web search capability.

    Args:
        state: Current state containing the product

    Returns:
        Updated state with the research report
    """
    llm = create_llm(
        model="glm-4-plus",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY"
    )

    # Bind the search tool to the LLM
    llm_with_tools = llm.bind_tools([{
        "name": "bocha_search",
        "description": "Search the web for information about the given query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"}
            },
            "required": ["query"]
        }
    }])

    prompt = f"""
    Conduct a comprehensive market analysis for the following product: {state['product']}.
    Include information about:
    - Target audience
    - Market size and potential
    - Competitors and their strengths/weaknesses
    - Current trends in the market
    - Pricing strategies of competitors
    - Potential challenges and opportunities

    Provide a detailed market research report.
    """

    # Initialize the conversation with the initial prompt
    messages = [{"role": "user", "content": prompt}]

    max_iterations = 5

    for iteration in range(max_iterations):
        # Invoke the LLM with the current conversation
        response = await llm_with_tools.ainvoke(messages)

        # Check if the response contains tool calls
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Add the assistant response that contains tool calls to messages
            messages.append(response)

            # Process each tool call
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'bocha_search':
                    query = tool_call['args']['query']
                    search_result = bocha_search(query)

                    # Append the search result as a ToolMessage
                    messages.append({
                        "role": "tool",
                        "content": search_result,
                        "name": tool_call['name'],
                        "tool_call_id": tool_call['id']
                    })
        else:
            # If no tool calls, treat this as the final report
            return {"research_report": response.content}

    # If we've reached max iterations, return the last response
    return {"research_report": response.content}


async def strategy_node(state: State) -> dict:
    """
    Formulates a marketing strategy based on the research report using GLM-5.1.

    Args:
        state: Current state containing the research report

    Returns:
        Updated state with the marketing strategy
    """
    llm = create_llm(
        model="glm-5.1",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        api_key_env="ZHIPU_API_KEY"
    )

    prompt = f"""
    Based on the following market research report, formulate a comprehensive marketing strategy for the product:

    {state['research_report']}

    Your strategy should include:
    - Target customer segments
    - Value proposition
    - Positioning strategy
    - Marketing channels to use
    - Key messaging points
    - Budget considerations
    - Success metrics
    - Timeline recommendations

    Provide a detailed marketing strategy document.
    """

    response = await llm.ainvoke(prompt)

    return {"strategy": response.content}


async def content_creator_node(state: State) -> dict:
    """
    Creates marketing content based on the strategy using Qwen3.7-Max.

    Args:
        state: Current state containing the marketing strategy

    Returns:
        Updated state with created content pieces
    """
    llm = create_llm(
        model="qwen3.7-max",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key_env="DASHSCOPE_API_KEY"
    )

    prompt = f"""
    Based on the following marketing strategy, create concrete marketing content pieces for the product:

    {state['strategy']}

    Please create the following content:
    - Social media campaign outline
    - Email marketing template
    - Blog post topics (at least 3)
    - Sample ad copy for 2 different platforms
    - Influencer collaboration ideas
    - Landing page content
    - Call-to-action suggestions

    Be creative and specific in your content recommendations.
    """

    response = await llm.ainvoke(prompt)

    return {"content": response.content}


def create_marketing_workflow():
    """
    Creates and compiles the LangGraph workflow for the marketing system.

    Returns:
        Compiled graph ready to run
    """
    # Create a state graph
    workflow = StateGraph(State)

    # Add nodes to the graph
    workflow.add_node("market_research", market_research_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("content_creator", content_creator_node)

    # Define edges
    workflow.add_edge(START, "market_research")
    workflow.add_edge("market_research", "strategy")
    workflow.add_edge("strategy", "content_creator")
    workflow.add_edge("content_creator", END)

    # Compile the graph
    return workflow.compile()


def save_results(product, research_report, strategy, content):
    """
    Saves the results to a markdown file in the output directory.

    Args:
        product (str): The product name
        research_report (str): The market research report
        strategy (str): The marketing strategy
        content (str): The created content

    Returns:
        str: The full file path of the saved file
    """
    # Ensure the output directory exists
    os.makedirs("output", exist_ok=True)

    # Sanitize the product name for filename
    sanitized_product = re.sub(r'[^a-zA-Z0-9]+', '-', product.strip().lower())
    sanitized_product = sanitized_product.strip('-')

    # Generate timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # Construct filename
    filename = f"{sanitized_product}_{timestamp}.md"
    filepath = os.path.join("output", filename)

    # Create the markdown content
    markdown_content = f"""Market Research Report for {product}
{research_report}

Marketing Strategy
{strategy}

Created Content
{content}"""

    # Write the file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return filepath


# Module-level compiled graph for import by app.py
marketing_graph = create_marketing_workflow()


async def run_marketing_workflow(product):
    """
    Runs the marketing workflow with the given product.

    Args:
        product (str): The product name to analyze

    Returns:
        dict: The result dictionary with research_report, strategy, and content
    """
    initial_state = {
        "product": product,
        "research_report": "",
        "strategy": "",
        "content": "",
        "error": ""
    }

    result = await marketing_graph.ainvoke(initial_state)
    return result


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Run the workflow
    print("Starting multi-agent marketing strategy generation...\n")

    result = asyncio.run(run_marketing_workflow("eco-friendly reusable water bottle"))

    # Print results
    print("="*60)
    print("MARKET RESEARCH REPORT")
    print("="*60)
    print(result["research_report"])
    print("\n")

    print("="*60)
    print("MARKETING STRATEGY")
    print("="*60)
    print(result["strategy"])
    print("\n")

    print("="*60)
    print("CONTENT CREATION")
    print("="*60)
    print(result["content"])
    print("\n")

    print("Marketing strategy generation completed!")

    # Save results to file
    file_path = save_results(
        result["product"],
        result["research_report"],
        result["strategy"],
        result["content"]
    )
    print(f"✅ All results saved to: {file_path}")
