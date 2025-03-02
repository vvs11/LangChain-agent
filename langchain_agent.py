from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from playwright.sync_api import sync_playwright

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# Define a browser interaction function
def browse_website(url: str) -> str:
    """Opens a URL using Playwright, scrolls, and extracts full page content."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(url, timeout=60000)  # 60s timeout

        # Automatically scroll down to load all content
        for _ in range(5):  
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            page.wait_for_timeout(2000)  

        content = page.content()
        browser.close()
        return content[:5000]  # Limit response to avoid long outputs

# Create a tool for browsing
browse_tool = Tool(
    name="Web Browser",
    func=browse_website,
    description="Fetches the webpage content of a given URL. No need to scroll manually.",
)

# Initialize an Agent with error handling
agent = initialize_agent(
    tools=[browse_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,  # ✅ Allows retrying on output parsing errors
    verbose=True
)

# Run an example query
response = agent.run("Open https://playwright.dev and summarize the webpage.")
print(response)
