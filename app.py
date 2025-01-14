import streamlit as st
import vertexai
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerativeModel,
    Part,
    Tool,
)
import requests
import os
import json
from google.cloud import aiplatform
from google.cloud import secretmanager
from google.oauth2 import service_account

# Initialize VertexAI with environment variables
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "agentic-ai-445703")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

def get_secret(secret_id: str) -> dict:
    """Get secret from Secret Manager."""
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return json.loads(response.payload.data.decode("UTF-8"))
    except Exception as e:
        st.error(f"Error accessing secret: {str(e)}")
        return None

# Initialize Google Cloud credentials
try:
    # Get service account key from Secret Manager
    sa_key = get_secret("currency-exchange-sa-key")
    if sa_key:
        credentials = service_account.Credentials.from_service_account_info(sa_key)
        vertexai.init(project=project_id, location=location, credentials=credentials)
    else:
        # Fallback to application default credentials
        vertexai.init(project=project_id, location=location)
        st.warning("Using application default credentials. Some features might be limited.")
except Exception as e:
    # Fallback to application default credentials
    vertexai.init(project=project_id, location=location)
    st.warning(f"Using application default credentials. Error: {str(e)}")

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

def get_currency_rate(user_query: str):
    """Process user query and return exchange rate information."""
    try:
        # Initialize the model with tools
        model = GenerativeModel("gemini-1.5-pro-001")
        
        # Create the chat
        chat = model.start_chat()
        
        # Generate response with function calling
        response = chat.send_message(
            f"""You are a helpful assistant that provides exchange rate information.
            Please help get the exchange rate for this request: {user_query}
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
                            return {
                                'from_currency': from_currency,
                                'to_currency': to_currency,
                                'rate': rate,
                                'success': True
                            }
    except Exception as e:
        st.error(f"Error processing request: {str(e)}")
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'Could not fetch exchange rate'}

# Streamlit UI
st.set_page_config(page_title="Currency Exchange Rate", page_icon="💱")

st.title("💱 Currency Exchange Rate Checker")
st.write("Ask about any currency exchange rate in natural language!")

# Display current configuration
with st.expander("Configuration Info"):
    st.write(f"Project ID: {project_id}")
    st.write(f"Location: {location}")
    if "gcp_service_account" in st.secrets:
        st.write("Authentication: Using service account")
    else:
        st.write("Authentication: Using application default credentials")

# Example queries
st.markdown("""
### Example queries:
- What's the exchange rate from USD to EUR?
- Convert Japanese Yen to British Pounds
- Show me the rate between Swiss Francs and Australian Dollars
""")

# User input
user_query = st.text_input(
    "Enter your query:",
    placeholder="e.g., What's the exchange rate from USD to EUR?"
)

# Process button
if st.button("Get Exchange Rate"):
    if user_query:
        with st.spinner("Getting exchange rate..."):
            result = get_currency_rate(user_query)
            
            if result['success']:
                st.success(f"Current exchange rate:")
                st.info(f"1 {result['from_currency']} = {result['rate']} {result['to_currency']}")
            else:
                st.error(f"Error: {result.get('error', 'Could not fetch exchange rate. Please try again with different currencies.')}") 