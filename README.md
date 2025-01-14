# Currency Exchange Rate Assistant with Gemini Function Calling 💱

This project demonstrates how to build a natural language currency exchange rate assistant using Google's Gemini Pro model with function calling capabilities. The application allows users to ask about exchange rates in natural language and get real-time responses.

<img src="https://github.com/vikas434/gemini-function-calling-demp/blob/main/demo-app.png?raw=true" alt="Currency Exchange App Demo" width="800"/>

## Table of Contents
- [Features](#features-)
- [Architecture](#architecture-)
- [Prerequisites](#prerequisites-)
- [Local Development Setup](#local-development-setup-)
- [Understanding Function Calling](#understanding-function-calling-)
- [Deployment Guide](#deployment-guide-)
- [FAQ and Troubleshooting](#faq-and-troubleshooting-)
- [Contributing](#contributing-)
- [License](#license-)


## Architecture 🏗️

The application uses the following components:

- **Frontend**: Streamlit web application
- **Backend**: Python with Vertex AI (Gemini Pro)
- **APIs**:
  - Gemini Pro for natural language processing
  - Frankfurter API for real-time exchange rates
- **Infrastructure**: Google Cloud Run
- **Security**: Google Cloud Secret Manager

## Prerequisites 📋

1. Google Cloud Account with billing enabled
2. Python 3.11 or higher
3. Google Cloud CLI installed
4. Required Google Cloud APIs enabled:
   - Vertex AI API
   - Cloud Run API
   - Secret Manager API
   - Cloud Build API

## Local Development Setup 🛠️

1. Clone the repository:
   ```bash
   git clone https://github.com/vikas434/gemini-function-calling-demp.git
   cd gemini-function-calling-demp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google Cloud credentials:
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

5. Run the application locally:
   ```bash
   streamlit run app.py
   ```

## Understanding Function Calling 🤖

Function calling is a powerful feature that allows the Gemini model to:
1. Understand natural language queries
2. Extract structured parameters
3. Call specific functions with those parameters

Example flow:
1. User asks: "What's the exchange rate from USD to EUR?"
2. Gemini extracts parameters:
   ```json
   {
     "from_currency": "USD",
     "to_currency": "EUR"
   }
   ```
3. These parameters are used to call the exchange rate API
4. Results are formatted and presented to the user

Key components in the code:
```python
# Function declaration for Gemini
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
```

## Deployment Guide 🚀

1. Enable required Google Cloud APIs:
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     aiplatform.googleapis.com \
     secretmanager.googleapis.com
   ```

2. Create a service account:
   ```bash
   gcloud iam service-accounts create currency-exchange-app \
     --display-name="Currency Exchange App Service Account"
   ```

3. Grant necessary permissions:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:currency-exchange-app@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

4. Set up Secret Manager:
   ```bash
   # Create and store the service account key
   gcloud secrets create currency-exchange-sa-key \
     --replication-policy="automatic"
   ```

5. Deploy to Cloud Run:
   ```bash
   gcloud run deploy currency-exchange-app \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## FAQ and Troubleshooting 🔍

### Q: Why am I getting authentication errors with Gemini?
**A**: This usually happens when:
- Billing is not enabled for your project
- The necessary APIs are not enabled
- The service account doesn't have the required permissions
Solution: Follow these steps:
1. Enable billing in Google Cloud Console
2. Enable the Vertex AI API
3. Ensure the service account has the 'aiplatform.user' role

### Q: The application shows "Using application default credentials"
**A**: This means:
- The service account key is not properly configured in Secret Manager
- The application cannot access the secret
Solution:
1. Verify the secret exists: `gcloud secrets list`
2. Check service account permissions
3. Ensure the secret name matches in your code

### Q: Exchange rates are not being fetched
**A**: Common causes:
- Invalid currency codes in the query
- Network connectivity issues
- Rate limiting from the Frankfurter API
Solution:
1. Use standard currency codes (EUR, USD, etc.)
2. Check your network connection
3. Implement rate limiting handling

### Q: Deployment to Cloud Run fails
**A**: Typical issues:
- Missing required APIs
- Insufficient permissions
- Build errors
Solution:
1. Enable all required APIs
2. Grant necessary permissions to the service account
3. Check build logs: `gcloud builds list`

## Contributing 🤝

Contributions are welcome<div align="center"><img src="https://github.com/vikas434/gemini-function-calling-demp/blob/main/demo-app.png?raw=true" alt="Currency Exchange App Demo" width="800"/></div>

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 👏

- Google Cloud Platform for Vertex AI and Cloud Run
- Frankfurter API for exchange rate data
- Streamlit for the web interface

---
Created with ❤️ using Google's Gemini Pro

