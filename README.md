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