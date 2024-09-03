import gradio as gr
import plotly.express as px
import requests
import os
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

GEMINI_PRO_API_KEY = os.getenv("GEMINI_API_KEY")


genai.configure(api_key=GEMINI_PRO_API_KEY)

def start_gemini_chat():
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = model.start_chat(
        history=[
            {"role": "user", "parts": "You are an AI storyteller. Generate a detailed and engaging story based on the user's prompts."},
            {"role": "model", "parts": "Great to meet you. What would you like to know?"}
        ]
    )
    return chat

def chatbot_response(history):

    chat = start_gemini_chat()

    user_message = history[-1][0]  
    response = chat.send_message(user_message)
    history[-1] = (user_message, response.text) 
    return history

def append_to_chat_input(chat_input, section_name, text_to_add):
    current_text = chat_input.get("text") if chat_input and "text" in chat_input else ""

    if current_text:
        if f"{section_name}:" in current_text:
            lines = current_text.split("\n")
            for i, line in enumerate(lines):
                if line.startswith(f"{section_name}:"):
                    lines[i] = f"{section_name}: {text_to_add}"
                    break
            new_text = "\n".join(lines)
        else:
            new_text = f"{current_text}\n{section_name}: {text_to_add}"
    else:
        new_text = f"{section_name}: {text_to_add}"

    return {"text": new_text}

def open_famous_stories():
    return gr.update(visible=True)

def handle_explore_btn(chat_input, tale):
    return append_to_chat_input(chat_input, "Story Origin", f"Adapt Well-known Tales: {tale}")

def launch_guided_storytelling(current_state):
    return gr.update(visible=False), gr.update(visible=True)

def back_to_main_interface(current_state):
    return gr.update(visible=True), gr.update(visible=False)

def append_guided_storytelling(chat_input, day, call_to_action, obstacles, emotions, helpers, resolution, growth):
    chat_input = append_to_chat_input(chat_input, "Describe the Day", day)
    chat_input = append_to_chat_input(chat_input, "Call to Action", call_to_action)
    chat_input = append_to_chat_input(chat_input, "Obstacles", obstacles)
    chat_input = append_to_chat_input(chat_input, "Emotions", emotions)
    chat_input = append_to_chat_input(chat_input, "Helpers", helpers)
    chat_input = append_to_chat_input(chat_input, "Resolution", resolution)
    chat_input = append_to_chat_input(chat_input, "Personal Growth", growth)
    
    return chat_input

def random_plot():
    df = px.data.iris()
    fig = px.scatter(df, x="sepal_width", y="sepal_length", color="species",
                    size='petal_length', hover_data=['petal_width'])
    return fig

def print_like_dislike(x: gr.LikeData):
    print(x.index, x.value, x.liked)

def add_message(history, message):
    if message["text"]:
        history.append((message["text"], None))
    for file in message["files"]:
        history.append(((file,), None))
    return history, gr.MultimodalTextbox(value=None, interactive=True)

with gr.Blocks(fill_height=True) as interface:
    current_state = gr.State(value="main")
    with gr.Column(visible=True) as main_interface:
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Story Origin")
                with gr.Row():
                    personal_btn = gr.Button("Personal Anecdote")
                    explore_btn = gr.Button("Adapt Well-known Tales")
                    famous_stories = gr.Column(visible=False)
                    with famous_stories:
                        cinderella_btn = gr.Button("Adaptation of Cinderella")
                        tortoise_btn = gr.Button("Adaptation of The Tortoise and the Hare")
                        moby_btn = gr.Button("Adaptation of Moby Dick")
                
                gr.Markdown("### Story Use Case")
                with gr.Row():
                    profile_btn = gr.Button("Profile Story")
                    social_media_btn = gr.Button("Social Media Content")
                
                gr.Markdown("### Story Time Frame")
                time_frame_btn = gr.Dropdown(choices=[f"{i}-{i+6} years" for i in range(8, 81, 7)])
                
                gr.Markdown("### Story Focus")
                focus_btn = gr.CheckboxGroup(choices=["Generosity", "Integrity", "Loyalty", "Devotion", "Kindness", "Sincerity", 
                                          "Self-control", "Confidence", "Persuasiveness", "Ambition", "Resourcefulness", 
                                          "Decisiveness", "Faithfulness", "Patience", "Determination", "Persistence", 
                                          "Fairness", "Cooperation", "Optimism", "Proactive", "Charisma", "Ethics", 
                                          "Relentlessness", "Authority", "Enthusiasm", "Boldness"])
                
                gr.Markdown("### Story Type")
                with gr.Row():
                    founding_story_btn = gr.Button("Where we came from: A founding Story")
                    case_for_change_btn = gr.Button("Why we can't stay here: A case-for-change story")
                    vision_story_btn = gr.Button("Where we're going: A vision story")
                    strategy_story_btn = gr.Button("How we're going to get there: A strategy story")
                    leadership_philosophy_btn = gr.Button("Why I lead the way I do: Leadership philosophy story")
                    rallying_story_btn = gr.Button("Why you should want to work here: A rallying story")
                    personal_stories_btn = gr.Button("Personal stories: Who you are, what you do, how you do it, and who you do it for")
                    values_story_btn = gr.Button("What we believe: A story about values")
                    customer_story_btn = gr.Button("Who we serve: A customer story")
                    sales_story_btn = gr.Button("What we do for our customers: A sales story")
                    marketing_story_btn = gr.Button("How we're different: A marketing story")
                with gr.Row():
                    gr.Markdown("### Guided Storytelling Framework")
                    guided_story_btn = gr.Button("Fill")

            with gr.Column(scale=1):
                gr.Markdown("### Gemini-powered Storytelling Chatbot")
                chatbot = gr.Chatbot(
                    elem_id="chatbot",
                    bubble_full_width=False,
                    height=600,
                    value=[]
                )
                chat_input = gr.MultimodalTextbox(
                    interactive=True,
                    file_count="multiple",
                    placeholder="Enter message or upload file...",
                    show_label=False
            )
                
    with gr.Column(visible=False) as guided_storytelling_interface:
        gr.Markdown("## Guided Storytelling Framework")
        with gr.Column():
            with gr.Row():
                day_input = gr.Textbox(lines=3, placeholder="Describe the day...", label="Describe the Day It Happened")
                call_to_action_input = gr.Textbox(lines=2, placeholder="What was the call to action?", label="Call to Action / Invitation")
                obstacles_input = gr.Textbox(lines=4, placeholder="Describe up to three obstacles...", label="Describing the Obstacles")
            with gr.Row():
                emotions_input = gr.Textbox(lines=4, placeholder="Describe emotions or fears...", label="Emotions / Fears Experienced")
                helpers_input = gr.Textbox(lines=3, placeholder="Who or what helped?", label="Recognize Helpers / Objects of Help")
                resolution_input = gr.Textbox(lines=3, placeholder="Describe the resolution...", label="Detailing the Resolution")
            with gr.Row():
                growth_input = gr.Textbox(lines=3, placeholder="Reflect on personal growth...", label="Reflecting on Personal Growth")
        with gr.Row():
            append_guided_btn = gr.Button("Append to Prompt")
            back_btn = gr.Button("Back to Main Interface")
            
        back_btn.click(back_to_main_interface, inputs=current_state, outputs=[main_interface, guided_storytelling_interface])
        append_guided_btn.click(append_guided_storytelling, 
                            inputs=[chat_input, day_input, call_to_action_input, obstacles_input, emotions_input, helpers_input, resolution_input, growth_input], 
                            outputs=chat_input)
 
    guided_story_btn.click(launch_guided_storytelling, inputs=current_state, outputs=[main_interface, guided_storytelling_interface])
    
    personal_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Origin"), gr.State("Personal Anecdote")], outputs=chat_input)
    explore_btn.click(open_famous_stories, outputs=famous_stories)
    cinderella_btn.click(handle_explore_btn, inputs=[chat_input, gr.State("Adaptation of Cinderella")], outputs=chat_input)
    tortoise_btn.click(handle_explore_btn, inputs=[chat_input, gr.State("Adaptation of The Tortoise and the Hare")], outputs=chat_input)
    moby_btn.click(handle_explore_btn, inputs=[chat_input, gr.State("Adaptation of Moby Dick")], outputs=chat_input)
    
    profile_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Use Case"), gr.State("Profile Story")], outputs=chat_input)
    social_media_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Use Case"), gr.State("Social Media Content")], outputs=chat_input)
    time_frame_btn.change(append_to_chat_input, inputs=[chat_input, gr.State("Story Time Frame"), time_frame_btn], outputs=chat_input)
    focus_btn.change(lambda c, f: append_to_chat_input(c, "Story Focus", ", ".join(f)), inputs=[chat_input, focus_btn], outputs=chat_input)
    founding_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Where we came from: A founding Story")], outputs=chat_input)
    case_for_change_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Why we can't stay here: A case-for-change story")], outputs=chat_input)
    vision_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Where we're going: A vision story")], outputs=chat_input)
    strategy_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("How we're going to get there: A strategy story")], outputs=chat_input)
    leadership_philosophy_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Why I lead the way I do: Leadership philosophy story")], outputs=chat_input)
    rallying_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Why you should want to work here: A rallying story")], outputs=chat_input)
    personal_stories_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Personal stories: Who you are, what you do, how you do it, and who you do it for")], outputs=chat_input)
    values_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("What we believe: A story about values")], outputs=chat_input)
    customer_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("Who we serve: A customer story")], outputs=chat_input)
    sales_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("What we do for our customers: A sales story")], outputs=chat_input)
    marketing_story_btn.click(append_to_chat_input, inputs=[chat_input, gr.State("Story Type"), gr.State("How we're different: A marketing story")], outputs=chat_input)

    
    chat_msg = chat_input.submit(add_message, [chatbot, chat_input], [chatbot, chat_input])
    bot_msg = chat_msg.then(chatbot_response, chatbot, chatbot)
    chatbot.like(print_like_dislike, None, None)
    
    

interface.launch()