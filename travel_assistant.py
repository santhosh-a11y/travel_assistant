import os
import streamlit as st
from google import genai
from google.genai import types

# Simple Page Setup
st.set_page_config(page_title="AI Travel Helper", page_icon="🌐")
st.title("🌐 AI Travel Guide")
st.caption("A helpful assistant with live Google Search to plan your trips.")

# Connect to Gemini (This will read your key from Streamlit secrets)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Simple rules for the AI (using clear, basic English)
TRAVEL_SYSTEM_PROMPT = """You are a helpful and simple travel guide. 
Your goal is to help people plan trips easily. 
Look at Google Search results to give real, up-to-date answers. 
Always look at the weather. If it rains, suggest indoor places to go. 
Give step-by-step plans. Explain how to travel from place to place easily. 
Use short sentences. Do not use difficult words or business language. 
Be friendly, direct, and clear so non-native English speakers can understand you perfectly."""

# Keep conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello traveler! I am your travel assistant. Tell me where you want to go. I can help you find good hotels, check the weather, choose transport, or make a daily plan."}
    ]

# Show past messages on screen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User input field
if user_prompt := st.chat_input("Where are we going next? (e.g., Tokyo weekend plan)"):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # Get answer from Gemini with live Google Search
    with st.chat_message("assistant"):
        with st.spinner("Checking maps and weather on Google..."):
            try:
                # Prepare history context
                contents = [
                    types.Content(role="user" if m["role"] == "user" else "model", 
                                  parts=[types.Part.from_text(text=m["content"])])
                    for m in st.session_state.messages
                ]
                
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=TRAVEL_SYSTEM_PROMPT,
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.3, # Lower temperature makes the text simpler and more factual
                    ),
                )
                agent_response = response.text
                st.write(agent_response)
                st.session_state.messages.append({"role": "assistant", "content": agent_response})
            except Exception as e:
                st.error(f"Could not connect to the network. Error: {str(e)}")
