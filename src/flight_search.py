# import asyncio
# import json
# from playwright.async_api import async_playwright
# from langchain.agents import initialize_agent
# from langchain_community.chat_models import ChatOpenAI
# from langchain.tools import Tool
# from urllib.parse import quote_plus

# async def scrape_flights(origin, destination, departure_date, return_date=None):
#     date_query = f"on {departure_date}" if not return_date else f"from {departure_date} to {return_date}"
#     url = f"https://www.google.com/travel/flights?q=flights+from+{quote_plus(origin)}+to+{quote_plus(destination)}+{quote_plus(date_query)}"
    
#     async with async_playwright() as p:
#         print("Launching Playwright browser...")
#         browser = await p.chromium.launch(headless=False, slow_mo=1000)  # Force non-headless mode, add delay
#         page = await browser.new_page()
#         print(f"Navigating to: {url}")
#         await page.goto(url)
#         await page.wait_for_timeout(5000)  # Wait for page to load
        
#         # Check if flights are available
#         flights = await page.query_selector_all("div[role='listitem']")
#         if not flights:
#             print("No flights found on the page.")
#             await browser.close()
#             return []

#         results = []
#         for flight in flights[:5]:  # Scrape top 5 cheapest flights
#             text = await flight.inner_text()
#             match = re.search(r'\$(\d+)', text)
#             price = int(match.group(1)) if match else None
#             if price:
#                 results.append(text)

#         print("Closing browser...")
#         await browser.close()
#         return results

# async def extract_flight_details(query: str, llm):
#     prompt = f"""
#     Extract the following details from the query:
#     - Origin city
#     - Destination city
#     - Departure date
#     - Return date (if mentioned)
    
#     Query: "{query}"
#     Provide the response in JSON format with keys: origin, destination, departure_date, return_date.
#     """
#     response = llm.invoke(prompt)  # Use invoke() instead of predict()
#     response_text = response.content  # Extract the actual response text
#     print("LLM Response:", response_text)
    
#     try:
#         details = json.loads(response_text)
#         return details.get("origin"), details.get("destination"), details.get("departure_date"), details.get("return_date")
#     except json.JSONDecodeError:
#         return None, None, None, None

# async def flight_tool(query: str):
#     print(f"Received query: {query}")
#     origin, destination, departure_date, return_date = await extract_flight_details(query, llm)

#     if not origin or not destination or not departure_date:
#         return "Please specify a valid origin, destination, and travel dates."
    
#     print(f"Extracted Origin: {origin}, Destination: {destination}, Departure: {departure_date}, Return: {return_date}")
#     flights = await scrape_flights(origin, destination, departure_date, return_date)

#     return flights if flights else "No flights found."

# # Set up LangChain Agent
# llm = ChatOpenAI(temperature=0)
# flight_search_tool = Tool(
#     name="Flight Search Tool",
#     func=lambda query: asyncio.run(flight_tool(query)),
#     description="Finds the cheapest flights given an origin, destination, and travel dates."
# )

# agent = initialize_agent([flight_search_tool], llm, agent="zero-shot-react-description", verbose=True)

# if __name__ == "__main__":
#     user_query = "Find me the cheapest one way flight from New York to London in April"
#     response = agent.run(user_query)
#     print(response)





import asyncio
import json
import re
from playwright.async_api import async_playwright
from langchain.agents import initialize_agent
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import Tool
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

async def scrape_flights(origin, destination, departure_date, return_date=None):
    date_query = f"on {departure_date}" if not return_date else f"from {departure_date} to {return_date}"
    url = f"https://www.google.com/travel/flights?q=flights+from+{quote_plus(origin)}+to+{quote_plus(destination)}+{quote_plus(date_query)}"
    
    async with async_playwright() as p:
        print("Launching Playwright browser...")
        browser = await p.chromium.launch(headless=True)  # Force non-headless mode, add delay
        page = await browser.new_page()
        print(f"Navigating to: {url}")
        await page.goto(url)
        await page.wait_for_timeout(5000)  # Wait for page to load
        
        # Debugging: Check if flight data is present
        content = await page.content()
        print("Page content snippet:", content[:1000])

        # Updated selector for flight details
        flights = await page.query_selector_all("div[role='listitem'], div[class*='U3gSDe']")
        if not flights:
            print("No flights found on the page. Double-check selector.")
            await browser.close()
            return []

        results = []
        cheapest_price = float('inf')
        cheapest_flight = None

        for flight in flights[:5]:  # Scrape top 5 cheapest flights
            text = await flight.inner_text()
            print("Flight Data:", text)  # Debugging
            match = re.search(r'([₹€£$]\s?\d{1,6}(?:,\d{3})*(?:\.\d{1,2})?)', text)
            if match:
                price_text = match.group(1).replace(',', '').strip()
                price_value = float(re.sub(r'[^0-9.]', '', price_text))
                if price_value < cheapest_price:
                    cheapest_price = price_value
                    cheapest_flight = text
                results.append(f"Price: {price_text}, Details: {text}")

        print("Closing browser...")
        await browser.close()
        return [cheapest_flight] if cheapest_flight else []

async def extract_flight_details(query: str, llm):
    prompt = f"""
    Extract the following details from the query:
    - Origin city
    - Destination city
    - Departure date
    - Return date (if mentioned)
    
    Query: "{query}"
    Provide the response in JSON format with keys: origin, destination, departure_date, return_date.
    """
    response = llm.invoke(prompt)  # Use invoke() instead of predict()
    response_text = response.content  # Extract the actual response text
    print("LLM Response:", response_text)
    
    try:
        details = json.loads(response_text)
        return details.get("origin"), details.get("destination"), details.get("departure_date"), details.get("return_date")
    except json.JSONDecodeError:
        return None, None, None, None

async def flight_tool(query: str):
    print(f"Received query: {query}")
    origin, destination, departure_date, return_date = await extract_flight_details(query, llm)

    if not origin or not destination or not departure_date:
        return "Please specify a valid origin, destination, and travel dates."
    
    print(f"Extracted Origin: {origin}, Destination: {destination}, Departure: {departure_date}, Return: {return_date}")
    flights = await scrape_flights(origin, destination, departure_date, return_date)

    if not flights:
        return f"No flights found for {origin} to {destination} on {departure_date}. Please check manually."
    
    return flights[0]  # Return the cheapest flight

# Set up LangChain Agent
llm = ChatOpenAI(temperature=0, openai_api_key=openai_api_key)
flight_search_tool = Tool(
    name="Flight Search Tool",
    func=lambda query: asyncio.run(flight_tool(query)),
    description="Finds the cheapest flights given an origin, destination, and travel dates."
)

agent = initialize_agent([flight_search_tool], llm, agent="zero-shot-react-description", verbose=True)

if __name__ == "__main__":
    user_query = "Find me the cheapest one way flight from New York to London in April. Also give me the airline details."
    response = agent.run(user_query)
    print(response)
