import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)
import requests
import json

# Initialize VertexAI
project_id = "agentic-ai-445703"
location = "us-central1"
vertexai.init(project=project_id, location=location)

def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Get the exchange rate between two currencies using the Frankfurter API."""
    url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['rates'][to_currency]
    return None

# Define the function declaration for currency conversion
get_exchange_rate_declaration = FunctionDeclaration(
    name="get_exchange_rate",
    description="Get the current exchange rate between two currencies",
    parameters={
        "type": "object",
        "properties": {
            "from_currency": {
                "type": "string",
                "description": "The source currency code (e.g., EUR, USD, JPY)"
            },
            "to_currency": {
                "type": "string",
                "description": "The target currency code (e.g., EUR, USD, JPY)"
            }
        },
        "required": ["from_currency", "to_currency"]
    }
)

# Create a tool with the function
tools = [Tool(function_declarations=[get_exchange_rate_declaration])]

def main():
    # Initialize the model with tools
    model = GenerativeModel("gemini-1.5-pro-001")
    
    # Example user query
    user_prompt = "What's the exchange rate from Japanese yen to British pounds today?"
    
    # Create the chat
    chat = model.start_chat()
    
    # Generate response with function calling
    response = chat.send_message(
        f"""You are a helpful assistant that provides exchange rate information.
        Please help get the exchange rate for this request: {user_prompt}
        Use the get_exchange_rate function to fetch the current rate.""",
        tools=tools
    )
    
    # Process the response
    if response.candidates:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.function_call:
                    # Get function call parameters
                    params = part.function_call.args
                    from_currency = params["from_currency"]
                    to_currency = params["to_currency"]
                    
                    # Call the actual function
                    rate = get_exchange_rate(from_currency, to_currency)
                    if rate:
                        print(f"Current exchange rate: 1 {from_currency} = {rate} {to_currency}")
                    else:
                        print("Could not fetch exchange rate")

if __name__ == "__main__":
    main() 