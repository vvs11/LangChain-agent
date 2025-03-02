from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
import os
import subprocess

# Initialize OpenAI Chat Model
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# Function to dynamically generate a Playwright script
def generate_flight_scraper_script(source, destination, month, website):
    """Generates a Python script for Playwright to scrape flights dynamically."""
    
    script_template = f"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def scrape_flights():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("{website}", timeout=60000)

        # Simulating user input for search
        try:
            page.fill('input[name="origin"]', "{source}")
            page.fill('input[name="destination"]', "{destination}")
            page.fill('input[name="month"]', "{month}")
            page.click('button[type="submit"]')
            page.wait_for_timeout(7000)  # Increase wait time for results to load
        except Exception as error:
            except Exception as e:
            print(f"Error interacting with website: {str(e)}")
            browser.close()
            return "Failed to retrieve flights."

        # Extract page content
        content = page.content()
        browser.close()
        
        # Parse flight information
        soup = BeautifulSoup(content, "html.parser")
        flights = []
        for flight in soup.find_all("div", class_="flight-option"):
            price_tag = flight.find("span", class_="flight-price")
            details_tag = flight.find("div", class_="flight-details")
            if price_tag and details_tag:
                price = price_tag.text.strip()
                details = details_tag.text.strip()
                flights.append((details, price))
        
        if not flights:
            return "No flights found."
        
        # Sort flights by price (handling non-numeric cases safely)
        flights.sort(key=lambda x: float(x[1].replace("$", "").replace(",", "")) if x[1].replace("$", "").replace(",", "").replace(".", "").isdigit() else float('inf'))
        return flights[:5]

if __name__ == "__main__":
    cheapest_flights = scrape_flights()
    if isinstance(cheapest_flights, str):
        print(cheapest_flights)
    else:
        for flight in cheapest_flights:
            print(f"Flight: {flight[0]} | Price: {flight[1]}")
"""
    return script_template

# Function to save and execute the script
def run_dynamic_scraper(source, destination, month, website):
    """Generates and runs the Playwright scraper dynamically."""
    script_code = generate_flight_scraper_script(source, destination, month, website)
    
    script_path = "flight_scraper.py"
    with open(script_path, "w") as file:
        file.write(script_code)
    
    # Run the generated script
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    
    return result.stdout

# Define input schema
class FlightScraperInput(BaseModel):
    source: str = Field(description="Source airport or city")
    destination: str = Field(description="Destination airport or city")
    month: str = Field(description="Month of travel")
    website: str = Field(description="Website URL to search flights")

# Define the tool using StructuredTool (ensures correct parsing)
flight_scraper_tool = StructuredTool.from_function(
    name="flight_scraper",
    func=run_dynamic_scraper,
    description="Finds the cheapest flights for a given source, destination, month, and website.",
    args_schema=FlightScraperInput,
)

# Initialize the LangChain Agent
agent = initialize_agent(
    tools=[flight_scraper_tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

# Run an example query
response = agent.run(
    "Find the cheapest flights from New York to San Francisco in April on https://www.google.com/flights."
)
print(response)
