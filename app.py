import openai
import streamlit as st
import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Auth0 Configurations (OAuth)
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
REDIRECT_URI = "https://abcd1234.ngrok.io/callback"  # Replace with your ngrok URL
AUTHORIZATION_URL = f"https://{AUTH0_DOMAIN}/authorize"
TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"

# Streamlit App
def authenticate_user():
    """Authenticate user with Auth0 via OAuth2"""
    auth0 = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, state = auth0.authorization_url(AUTHORIZATION_URL)

    if "code" not in st.query_params:
        st.write(f"Please log in to proceed by clicking [here]({authorization_url})")
        return False

    else:
        authorization_response = st.query_params["code"][0]
        token = auth0.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=authorization_response)
        user_info = auth0.get(f"https://{AUTH0_DOMAIN}/userinfo").json()
        st.session_state.user_info = user_info
        return True

# Define OpenAI functions
def generate_interview_question():
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="Ask an interview question for a software engineer position.",
        max_tokens=100,
        temperature=0.7
    )
    return response.choices[0].text.strip()

def evaluate_answer(answer):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Evaluate the following answer to an interview question: {answer}",
        max_tokens=150,
        temperature=0.5
    )
    return response.choices[0].text.strip()

# Streamlit UI
def main():
    st.title("AI-Powered Mock Interview")

    if not authenticate_user():
        return

    user_info = st.session_state.user_info
    st.image(user_info['picture'], width=100)
    st.write(f"Welcome {user_info['name']}!")
    st.write(f"Email: {user_info['email']}")

    if st.button("Start Interview"):
        question = generate_interview_question()
        st.write(question)

    answer = st.text_area("Your Answer")

    if st.button("Submit Answer") and answer:
        evaluation = evaluate_answer(answer)
        st.subheader("Evaluation")
        st.write(evaluation)

if __name__ == "__main__":
    main()

