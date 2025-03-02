from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool
from playwright.sync_api import sync_playwright
import os
import json

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Define the function to generate Playwright script dynamically
def generate_playwright_script(query: str) -> str:
    """Generates a Playwright script based on the query using OpenAI."""
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
    prompt = f"""
    Write a Playwright script in Python that automates the browser to accomplish this task:
    "{query}"
    The script should:
    - Open Google in headless mode
    - Search for the query
    - Extract the top results
    - Print the extracted data in JSON format
    Do not include explanations, only return valid Python code.
    """
    response = llm.predict(prompt)
    return response

# Define the function to execute Playwright script
def execute_playwright_script(script: str) -> dict:
    """Executes the generated Playwright script and extracts the JSON output."""
    script_path = "temp_script.py"
    with open(script_path, "w") as f:
        f.write(script)
    
    try:
        output = os.popen(f"python {script_path}").read()
        json_output = json.loads(output)
        return json_output
    except Exception as e:
        return {"error": str(e)}
    finally:
        os.remove(script_path)

# Define the LangChain tool to interact with Playwright
def playwright_tool(query: str) -> dict:
    """Generates and executes a Playwright script based on user query."""
    script = generate_playwright_script(query)
    result = execute_playwright_script(script)
    return result

# Define the LangChain agent
def create_agent():
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)
    
    tools = [
        Tool(
            name="Playwright Automation",
            func=playwright_tool,
            description="Use this tool to automate browser tasks and extract data."
        )
    ]
    
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    return agent

# Example Usage
if __name__ == "__main__":
    agent = create_agent()
    query = "Find me the cheapest flight from London to Dubai in April."
    result = agent.run(query)
    print("Agent Result:", result)
