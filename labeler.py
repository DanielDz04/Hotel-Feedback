
import requests
import streamlit as st

MODEL = "openai/gpt-oss-20b"
URL = "https://api.groq.com/openai/v1/chat/completions"

CATEGORIES = [
    "Room Cleanliness",
    "Staff & Service",
    "Facilities",
    "Value for Money",
    "Other"
]

def label_comment(text):
    prompt = f"""
You are analyzing guest feedback for StayWise Hotel.

Classify the following comment into exactly ONE category:

- Room Cleanliness: Cleanliness, hygiene, and housekeeping.
- Staff & Service: Employee behavior and customer service.
- Facilities: Wi-Fi, parking, pool, gym, and hotel amenities.
- Value for Money: Prices, charges, and overall value.
- Other: Comments that do not fit the categories above.

If multiple categories apply, choose the main issue.

Reply with ONLY the category name.

Comment: {text}
"""

    response = requests.post(
        URL,
        headers={
            "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"
        },
        json={
            "model": MODEL,
            "temperature": 0,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        },
        timeout=30
    )

    response.raise_for_status()

    answer = response.json()["choices"][0]["message"]["content"]
    label = answer.strip()

    return label if label in CATEGORIES else "Other"
