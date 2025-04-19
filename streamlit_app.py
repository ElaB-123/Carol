import streamlit as st
from openai import OpenAI
import json
from datetime import datetime

# Show title and description
st.title("🏋️‍♂️ Fitness Coach Bot")
st.write(
    "Welcome to your personal AI fitness coach! I can help you with:\n"
    "- Creating personalized workout plans\n"
    "- Setting and tracking fitness goals\n"
    "- Modifying exercises based on injuries\n"
    "- Tracking your progress\n"
    "- Providing form guidance and exercise explanations"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "fitness_profile" not in st.session_state:
    st.session_state.fitness_profile = {
        "goals": [],
        "injuries": [],
        "fitness_level": "",
        "preferences": [],
        "workout_history": []
    }

# Ask user for their OpenAI API key
openai_api_key = st.secrets["OPENAI_API_KEY"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    # Sidebar for fitness profile
    with st.sidebar:
        st.header("Your Fitness Profile")
        
        # Fitness Level
        fitness_level = st.selectbox(
            "What's your current fitness level?",
            ["Beginner", "Intermediate", "Advanced"]
        )
        st.session_state.fitness_profile["fitness_level"] = fitness_level

        # Goals
        goals = st.multiselect(
            "What are your fitness goals?",
            ["Weight Loss", "Muscle Gain", "Endurance", "Flexibility", "Strength", "General Fitness"]
        )
        st.session_state.fitness_profile["goals"] = goals

        # Injuries
        injuries = st.multiselect(
            "Do you have any injuries or limitations?",
            ["None", "Back Pain", "Knee Issues", "Shoulder Problems", "Ankle Issues", "Other"]
        )
        st.session_state.fitness_profile["injuries"] = injuries

        # Preferences
        preferences = st.multiselect(
            "What type of workouts do you prefer?",
            ["Cardio", "Strength Training", "Yoga", "HIIT", "Sports", "Outdoor Activities"]
        )
        st.session_state.fitness_profile["preferences"] = preferences

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about fitness, workouts, or your goals!"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Create system message with fitness context
        system_message = {
            "role": "system",
            "content": f"""You are an expert fitness coach. The user's profile is:
            - Fitness Level: {st.session_state.fitness_profile['fitness_level']}
            - Goals: {', '.join(st.session_state.fitness_profile['goals'])}
            - Injuries/Limitations: {', '.join(st.session_state.fitness_profile['injuries'])}
            - Preferences: {', '.join(st.session_state.fitness_profile['preferences'])}
            
            Provide detailed, personalized fitness advice. Include:
            1. Specific exercise recommendations
            2. Form guidance
            3. Modifications for any injuries
            4. Progress tracking suggestions
            5. Motivation and encouragement
            
            Always consider safety first and provide modifications when needed."""
        }

        # Generate response
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[system_message] + [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Track workout history
        if "workout" in prompt.lower() or "exercise" in prompt.lower():
            st.session_state.fitness_profile["workout_history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": prompt,
                "response": response
            })
