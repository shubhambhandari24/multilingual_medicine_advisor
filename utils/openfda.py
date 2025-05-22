import requests

OPENFDA_ENDPOINT = "https://api.fda.gov/drug/label.json"

def get_medicine_info(query):
    try:
        response = requests.get(OPENFDA_ENDPOINT, params={"search": f"description:{query}", "limit": 1})
        data = response.json()
        return data["results"][0]["description"][0]
    except Exception as e:
        return f"API error: {e}"
