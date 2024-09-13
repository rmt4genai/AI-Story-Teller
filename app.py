import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

GEMINI_PRO_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_PRO_API_KEY)

st.title("✨ AI Storyteller: Craft, Enhance, and Polish Your Stories")

def start_gemini_chat():
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(
        history=[
            {"role": "user", "parts": "You are an AI storyteller. Generate a detailed and engaging story based on the user's prompts."},
            {"role": "model", "parts": "Great to meet you. I'm ready to help you create engaging stories based on your inputs. What would you like to start with?"}
        ]
    )
    return chat

def chatbot_response(chat, user_message):
    response = chat.send_message(user_message)
    return response.text


if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat' not in st.session_state:
    st.session_state.chat = start_gemini_chat()
if 'current_prompt' not in st.session_state:
    st.session_state.current_prompt = ""
if 'first_draft' not in st.session_state:
    st.session_state.first_draft = ""
if 'current_tier' not in st.session_state:
    st.session_state.current_tier = "TIER-1" 
if 'page' not in st.session_state:
    st.session_state.page = None
if 'enhanced_story' not in st.session_state:
    st.session_state.enhanced_story = ""

def switch_tier(selected_tier):
    st.session_state.current_tier = selected_tier

tier = st.sidebar.radio(
    "Select Tier:", 
    ["TIER-1", "TIER-2", "TIER-3"], 
    index=["TIER-1", "TIER-2", "TIER-3"].index(st.session_state.current_tier),
    key="tier_selector", 
    on_change=lambda: switch_tier(st.session_state.tier_selector)
)

if st.session_state.current_tier == "TIER-1":

    col1, col2 = st.columns(2)

    with col1:
        st.header("Story Options")
        
        def update_current_prompt():
            prompt = f"Story Origin: {st.session_state.origin}\n"
            if st.session_state.origin == 'Adapt Well-known Tales':
                prompt += f"Tale: {st.session_state.tale}\n"
            prompt += f"Story Use Case: {st.session_state.use_case}\n"
            prompt += f"Story Time Frame: {st.session_state.time_frame}\n"
            prompt += f"Story Focus: {', '.join(st.session_state.focus)}\n"
            prompt += f"Story Type: {st.session_state.story_type}\n"

            if st.session_state.show_guided_storytelling:
                prompt += "Guided Storytelling Framework:\n"
                for key, value in st.session_state.guided_story_inputs.items():
                    if value:
                        prompt += f"{key.capitalize()}: {value}\n"

            st.session_state.current_prompt = prompt.strip()

        st.session_state.origin = st.radio("Choose origin:", ["Personal Anecdote", "Adapt Well-known Tales"], on_change=update_current_prompt)

        if st.session_state.origin == "Adapt Well-known Tales":
            st.session_state.tale = st.selectbox("Select a tale:", ["Adaptation of Cinderella", "Adaptation of The Tortoise and the Hare", "Adaptation of Moby Dick"], on_change=update_current_prompt)

        st.session_state.use_case = st.radio("Choose use case:", ["Profile Story", "Social Media Content"], on_change=update_current_prompt)
        st.session_state.time_frame = st.selectbox("Select time frame:", [f"{i}-{i+6} years" for i in range(8, 81, 7)], on_change=update_current_prompt)
        focus_options = ["Generosity", "Integrity", "Loyalty", "Devotion", "Kindness", "Sincerity", 
                        "Self-control", "Confidence", "Persuasiveness", "Ambition", "Resourcefulness", 
                        "Decisiveness", "Faithfulness", "Patience", "Determination", "Persistence", 
                        "Fairness", "Cooperation", "Optimism", "Proactive", "Charisma", "Ethics", 
                        "Relentlessness", "Authority", "Enthusiasm", "Boldness"]
        st.session_state.focus = st.multiselect("Select focus:", focus_options, on_change=update_current_prompt)
        story_types = [
            "Where we came from: A founding Story",
            "Why we can't stay here: A case-for-change story",
            "Where we're going: A vision story",
            "How we're going to get there: A strategy story",
            "Why I lead the way I do: Leadership philosophy story",
            "Why you should want to work here: A rallying story",
            "Personal stories: Who you are, what you do, how you do it, and who you do it for",
            "What we believe: A story about values",
            "Who we serve: A customer story",
            "What we do for our customers: A sales story",
            "How we're different: A marketing story"
        ]
        st.session_state.story_type = st.selectbox("Choose story type:", story_types, on_change=update_current_prompt)

        if 'show_guided_storytelling' not in st.session_state:
            st.session_state.show_guided_storytelling = False
        if 'guided_story_inputs' not in st.session_state:
            st.session_state.guided_story_inputs = {
                'day': '', 'call_to_action': '', 'obstacles': '',
                'emotions': '', 'helpers': '', 'resolution': '', 'growth': ''
            }

        if st.checkbox("Use Guided Storytelling Framework", value=st.session_state.show_guided_storytelling):
            st.session_state.show_guided_storytelling = True
            st.subheader("Guided Storytelling Framework")
            for key in st.session_state.guided_story_inputs:
                st.session_state.guided_story_inputs[key] = st.text_area(f"{key.capitalize()}:", value=st.session_state.guided_story_inputs[key], on_change=update_current_prompt)
        else:
            st.session_state.show_guided_storytelling = False

        update_current_prompt()

    with col2:
        st.header("Chat Interface")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        edited_prompt = st.text_area("Edit your story idea here:", value=st.session_state.current_prompt, height=200)

        if st.button("Send"):
            if edited_prompt:
                st.chat_message("user").markdown(edited_prompt)
                st.session_state.messages.append({"role": "user", "content": edited_prompt})

                try:
                    response = chatbot_response(st.session_state.chat, edited_prompt)
                    with st.chat_message("assistant"):
                        st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})

                    # Store the first draft
                    st.session_state.first_draft = response  # Save response as first draft
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chat = start_gemini_chat()
            st.experimental_rerun()

        # Add button to save story as first draft
        if st.button("Save as First Draft"):
            if st.session_state.messages:
                # Save the last assistant's message (the story) as the first draft
                for message in reversed(st.session_state.messages):
                    if message["role"] == "assistant":
                        st.session_state.first_draft = message["content"]
                        st.success("Story saved as first draft for Tier-2 enhancement!")
                        break
            else:
                st.warning("No story has been generated yet!")

if st.session_state.current_tier == "TIER-2":
    st.subheader("🎉 Congratulations on completing your first draft!")
    st.write("Select an option to enhance your story:")

    st.write("### Your First Draft")
    st.text_area("First Draft", value=st.session_state.first_draft, height=150, disabled=True)

    st.write("### Option 1: Personalized Coaching")
    if st.button("Book a Session with a Storytelling Coach"):
        st.session_state.page = "booking"

    st.write("### Option 2: Enhance Your Story with Advanced Structures")
    selected_structure = st.selectbox("Choose a storytelling structure:", [
        "The Story Hanger", "The Story Spine", "Hero's Journey", "Beginning to End", "In Media Res", "Nested Loops", "The Cliffhanger"
    ])

    structure_descriptions = {
    "The Story Hanger": "Begin with a compelling hook to grab attention. Set up a significant goal for the protagonist and introduce obstacles that create tension. The inciting incident should make the audience care about the stakes and the protagonist’s journey.",
    "The Story Spine": "Follow a structured sequence: 'Once Upon a Time' sets the stage, 'Everyday' describes the norm, 'Till One Day' introduces a change, 'Because of That' shows consequences, 'Until Finally' reveals the climax, and 'And Ever Since Then' concludes with the outcome.",
    "Hero's Journey": "Outline the hero's adventure through stages: 'Situation' starts the journey, 'Complication' presents challenges, 'Solution' resolves the problem, and 'Resolution' concludes with the hero's transformation and new status quo.",
    "Beginning to End": "Adopt a traditional narrative flow with a clear beginning, middle, and end. This straightforward approach guides the audience through a structured story progression from introduction to resolution.",
    "In Media Res": "Start the story in the midst of a dramatic or crucial moment, skipping the initial setup. This approach engages the audience immediately by placing them directly into the action or conflict before providing background context.",
    "Nested Loops": "Embed smaller stories or anecdotes within the main narrative. This technique provides additional perspectives or background information, enriching the primary storyline and adding depth to the narrative.",
    "The Cliffhanger": "End the story or segment on a suspenseful or unresolved note to keep the audience intrigued and eager for more. This technique is effective for creating anticipation and maintaining engagement."
}

    st.write(structure_descriptions[selected_structure])

    if st.button("Enhance Story"):
        enhanced_story_prompt = f"Please enhance the following first draft using the '{selected_structure}' structure:\n\n"
        enhanced_story_prompt += st.session_state.first_draft  # Use the first draft
        try:
            response = chatbot_response(st.session_state.chat, enhanced_story_prompt)
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.enhanced_story = response
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat = start_gemini_chat()
        st.experimental_rerun()

if 'page' in st.session_state and st.session_state.page == "booking":
    st.title("📅 Book a Session with a Storytelling Coach")

    with st.form(key='booking_form'):
        st.write("Please fill out the details below to book a session.")
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        
  
        preferred_date = st.date_input("Preferred Date")
        preferred_time = st.time_input("Preferred Time", value=datetime.now().time())  # Clock-like widget

        submit_button = st.form_submit_button(label="Submit Booking Request")

        if submit_button:
            st.session_state.page = None  
            st.success("Your appointment request has been sent! Our team will get back to you shortly.")

if st.session_state.current_tier == "TIER-3":
    st.header("✨ Story Polishing: Final Touches")

    if 'final_draft' not in st.session_state:
        st.session_state.final_draft = st.session_state.get("enhanced_story", "No enhanced story available from Tier-2")

    st.write("### Your Enhanced Story from Tier-2:")
    st.text_area("Enhanced Story", value=st.session_state.final_draft, height=300, disabled=True)

    st.sidebar.header("Polishing Options")

    polishing_option = st.sidebar.selectbox("Choose what to add to your story:", [
        "Add Impactful Quotes/Poems",
        "Add Similes/Comparisons",
        "Generate Creative Enhancements",
        "Receive Emotional Resonance Tips"
    ])

    def generate_ai_tip(tip_type, story_text):

        prompt_map = {
            "quote": f"Generate an impactful quote for this story:\n\n{story_text}",
            "simile": f"Generate a simile for the following story:\n\n{story_text}",
            "creative": f"Generate a creative enhancement for the story:\n\n{story_text}",
            "emotional": f"Provide an emotional resonance tip for this story:\n\n{story_text}"
        }

        prompt = prompt_map.get(tip_type, "")
        if prompt:
            response = chatbot_response(st.session_state.chat, prompt)
            return response
        return ""

    if polishing_option == "Add Impactful Quotes/Poems":
        st.sidebar.subheader("Add Impactful Quotes/Poems")
        if st.sidebar.button("Generate Quote/Poem"):
            quote = generate_ai_tip("quote", st.session_state.final_draft)
            st.write(f"**Quote/Poem Suggestion**: {quote}")
            st.session_state.final_draft += f"\n\n{quote}"
            st.success("Quote/Poem added to your story!")

    elif polishing_option == "Add Similes/Comparisons":
        st.sidebar.subheader("Add Similes/Comparisons")
        if st.sidebar.button("Generate Simile/Comparison"):
            simile = generate_ai_tip("simile", st.session_state.final_draft)
            st.write(f"**Simile/Comparison**: {simile}")
            st.session_state.final_draft += f"\n\n{simile}"
            st.success("Simile/Comparison added to your story!")

    elif polishing_option == "Generate Creative Enhancements":
        st.sidebar.subheader("Generate Creative Enhancements")
        if st.sidebar.button("Generate Creative Lines/Descriptions"):
            creative_line = generate_ai_tip("creative", st.session_state.final_draft)
            st.write(f"**Creative Description**: {creative_line}")
            st.session_state.final_draft += f"\n\n{creative_line}"
            st.success("Creative enhancement added to your story!")

    elif polishing_option == "Receive Emotional Resonance Tips":
        st.sidebar.subheader("Emotional Resonance Tips")
        if st.sidebar.button("Generate Tips"):
            emotional_tip = generate_ai_tip("emotional", st.session_state.final_draft)
            st.write(f"**Emotional Resonance Tip**: {emotional_tip}")
            st.success("Tip displayed. Apply it to your story to enhance its emotional impact!")

    st.write("### Final Draft:")
    st.text_area("Final Draft", value=st.session_state.final_draft, height=300)

    if st.button("Save Final Story"):
        file_path = "final_draft.txt"
        with open(file_path, "w") as file:
            file.write(st.session_state.final_draft)
        st.success(f"Your polished story has been saved to {file_path}!")
        st.download_button("Download Final Draft", data=open(file_path, "r").read(), file_name=file_path)
