# LangChain-agent
A LangChain agent PoC
Follow these steps to run the agent:


1. clone repo

2. Navigate to src folder 
    ```
    cd src
    ```

3. create a .env file and add the following content to it 
    ```
    OPENAI_API_KEY=YOUR_OPENAI_KEY
    ```
    Make sure to add your Open API Key in the file

4. Install Dependencies 

    ```
    pip install langchain langchain-openai playwright beautifulsoup4 pydantic
    
    playwright install

    pip install langchain-community

    pip install python-dotenv
    
    ```

5. Run the following files as agents:

    ```
    python langchain_agent.py
    ```

6. Every file has a prompt for which it works. Search for 'user_query' in the file to get the prompt
7. By default the browsers are headless. If you want to see the browser perform the actions, search for 'headless' and set to 'True'
