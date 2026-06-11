import streamlit as st

import random

import sqlite3

import io

import contextlib

import math

import os



from openai import OpenAI

from datetime import datetime

from dotenv import load_dotenv



from PIL import Image, ImageDraw, ImageFont



st.set_page_config(

    page_title="Python Buddy",

    page_icon="🐍",

    layout="wide"

)





st.markdown("""

<style>



/* MAIN BACKGROUND */



.stApp {



    background: linear-gradient(

        135deg,

        #ffe4ec,

        #f3d9fa,

        #e9d5ff

    );



    color: #2d1b3d;

}



/* TITLE */



.title {



    text-align: center;



    font-size: 60px;



    font-weight: bold;



    color: #a855f7;



    animation: glow 2s infinite alternate;

}



.subtitle {



    text-align: center;



    color: #4b5563;



    font-size: 20px;



    margin-bottom: 20px;

}



/* GLOW ANIMATION */



@keyframes glow {



    from {

        text-shadow: 0 0 12px #d946ef;

    }



    to {

        text-shadow: 0 0 30px #c084fc;

    }

}



/* CARD DESIGN */



.card {



    background: rgba(255, 255, 255, 0.75);



    padding: 25px;



    border-radius: 22px;



    margin-top: 20px;



    transition: 0.3s;



    border: 1px solid rgba(255,255,255,0.5);



    backdrop-filter: blur(14px);



    color: #2d1b3d;

}



.card:hover {



    transform: translateY(-8px);



    box-shadow: 0 0 25px rgba(168,85,247,0.35);

}



/* BUTTON */



.stButton button {



    width: 100%;



    height: 50px;



    border-radius: 14px;



    font-size: 18px;



    font-weight: bold;



    background: linear-gradient(

        to right,

        #ec4899,

        #a855f7

    );



    color: white;



    border: none;



    transition: 0.3s;

}



.stButton button:hover {



    transform: scale(1.03);



    box-shadow: 0 0 20px #d946ef;

}



/* INPUT FIELDS */



.stTextInput input,

.stTextArea textarea {



    border-radius: 14px;



    border: 2px solid #d946ef;



    background-color: rgba(255,255,255,0.8);



    color: #2d1b3d;

}



/* SIDEBAR */



section[data-testid="stSidebar"] {



    background: linear-gradient(

        180deg,

        #fbcfe8,

        #e9d5ff

    );

}



/* CHAT */



[data-testid="stChatMessage"] {



    background-color: rgba(255,255,255,0.6);



    border-radius: 15px;



    padding: 10px;



    margin-bottom: 10px;

}



/* METRICS */



[data-testid="metric-container"] {



    background: rgba(255,255,255,0.6);



    border-radius: 15px;



    padding: 15px;

}



/* SLIDER */



.stSlider {



    padding-top: 20px;

}



</style>

""", unsafe_allow_html=True)





conn = sqlite3.connect(

    "users.db",

    check_same_thread=False

)



cursor = conn.cursor()



cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    username TEXT,

    password TEXT

)

""")



conn.commit()







# Only use .env for API key configuration.

load_dotenv()

openai_api_key = (

    st.secrets.get("OPENAI_API_KEY")

    or os.getenv("OPENAI_API_KEY")

)



if not openai_api_key:

    st.error(

        "OpenAI API key not found. Add OPENAI_API_KEY to .streamlit/secrets.toml or .env, or set the OPENAI_API_KEY environment variable."

    )

    st.stop()



client = OpenAI(

    api_key=openai_api_key

)



def ask_ai(prompt):



    response = client.chat.completions.create(



        model="gpt-4o-mini",



        messages=[

            {

                "role": "system",

                "content": """

                You are an expert Python tutor.



                Explain clearly.

                Beginner friendly.

                Give examples.

                Fix coding mistakes.

                Never give wrong code.

                """

            },



            {

                "role": "user",

                "content": prompt

            }

        ]

    )



    return response.choices[0].message.content





def ask_model_with_fallback(prompt, provider):



    provider_key_map = {

        "Gemini": os.getenv("GEMINI_API_KEY"),

        "GROQ": os.getenv("GROQ_API_KEY"),

        "OpenAI": openai_api_key

    }



    provider_model_map = {

        "Gemini": "gemini-1.5",

        "GROQ": "groq-1",

        "OpenAI": "gpt-4o-mini"

    }



    provider_key = provider_key_map.get(provider)

    provider_model = provider_model_map.get(provider)



    if provider != "OpenAI" and not provider_key:

        return ask_ai(prompt)



    try:

        client = OpenAI(api_key=provider_key)

        response = client.chat.completions.create(

            model=provider_model,

            messages=[

                {

                    "role": "system",

                    "content": (

                        "You are a helpful Python learning assistant that uses LangGraph and LangChain concepts. "

                        "Explain Python ideas clearly and connect related concepts as a graph."

                    )

                },

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

        return response.choices[0].message.content



    except Exception as e:

        if provider != "OpenAI" and openai_api_key:

            try:

                fallback_response = ask_ai(prompt)

                return (

                    f"⚠️ {provider} model call failed: {e}\n\n"

                    "Falling back to OpenAI...\n\n"

                    f"{fallback_response}"

                )

            except Exception as fallback_error:

                return (

                    f"⚠️ {provider} model call failed: {e}\n\n"

                    f"Fallback to OpenAI also failed: {fallback_error}"

                )

        raise







st.markdown(

    '<p class="title">🐍 Python Buddy</p>',

    unsafe_allow_html=True

)



st.markdown(

    '<p class="subtitle">AI Powered Python Learning Platform</p>',

    unsafe_allow_html=True

)





if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if "username" not in st.session_state:

    st.session_state.username = "Guest"



if "messages" not in st.session_state:

    st.session_state.messages = []
    





if True:



    st.sidebar.success(

        f"Welcome {st.session_state.username}"

    )



    menu = st.sidebar.selectbox(

        "Choose Feature",

        [

            "🏠 Dashboard",

            "🤖 AI Chatbot",

            "💻 Code Practice",

            "🐞 Debug Errors",

            "🧠 Quiz"

        ]

    )



   



    if menu == "🏠 Dashboard":



       

        st.title("📊 Dashboard")



        col1, col2, col3 = st.columns(3)



        with col1:

            st.metric(

                "Exercises Completed",

                "12"

            )



        with col2:

            st.metric(

                "Quiz Score",

                "85%"

            )



        with col3:

            st.metric(

                "Certificates Earned",

                "2"

            )



        st.markdown("---")



        st.subheader("🔥 Learning Progress")



        progress = st.slider(

            "Python Progress",

            0,

            100,

            70

        )



        st.progress(progress)



        st.markdown(

            '</div>',

            unsafe_allow_html=True

        )





    elif menu == "🤖 AI Chatbot":



        



        st.subheader("🤖 AI Python Tutor")



        user_input = st.chat_input(

            "Ask Any Python Question"

        )



        if user_input:



            st.session_state.messages.append(

                {

                    "role": "user",

                    "content": user_input

                }

            )



            ai_reply = ask_ai(user_input)



            st.session_state.messages.append(

                {

                    "role": "assistant",

                    "content": ai_reply

                }

            )



        for msg in st.session_state.messages:



            with st.chat_message(msg["role"]):



                st.write(msg["content"])



        st.markdown(

            '</div>',

            unsafe_allow_html=True

        )



    

    elif menu == "💻 Code Practice":



      



        st.subheader("💻 Practice Python Code")



        code = st.text_area(

            "Write Python Code",

            height=250

        )



        if st.button("Run Code"):



            output = io.StringIO()



            try:



                with contextlib.redirect_stdout(output):



                    exec(code)



                st.success(

                    "Code Executed Successfully"

                )



                st.code(

                    output.getvalue(),

                    language="python"

                )



            except Exception as e:



                st.error(f"Error: {e}")



        st.markdown(

            '</div>',

            unsafe_allow_html=True

        )



   



    elif menu == "🐞 Debug Errors":



       


        st.subheader("🐞 Debug Python Errors")



        buggy_programs = [



            {

                "buggy": """

for i in range(5)

    print(i)

""",



                "correct": """

for i in range(5):

    print(i)

"""

            },



            {

                "buggy": """

name = Vaishnavi

print(name)

""",



                "correct": """

name = "Vaishnavi"

print(name)

"""

            }

        ]



        selected_bug = random.choice(

            buggy_programs

        )



        st.code(

            selected_bug["buggy"],

            language="python"

        )



        user_fix = st.text_area(

            "Fix The Code"

        )



        if st.button("Check Fix"):



            if user_fix.strip() == selected_bug["correct"].strip():



                st.success("Correct Fix 🎉")



            else:



                st.error("Wrong Fix ❌")



                st.code(

                    selected_bug["correct"],

                    language="python"

                )



        st.markdown(

            '</div>',

            unsafe_allow_html=True

        )



    



    elif menu == "🧠 Quiz":



        



        st.subheader("🧠 Python Quiz")



        quiz_questions = [



            {

                "question": "Which keyword creates function?",

                "options": [

                    "func",

                    "def",

                    "function",

                    "create"

                ],

                "answer": "def"

            },



            {

                "question": "Which symbol is used for comments?",

                "options": [

                    "#",

                    "//",

                    "/*",

                    "--"

                ],

                "answer": "#"

            }

        ]



        score = 0



        for i, q in enumerate(quiz_questions):



            st.write(q["question"])



            selected = st.radio(

                "Choose Answer",

                q["options"],

                key=i

            )



            if selected == q["answer"]:



                score += 1



        if st.button("Submit Quiz"):



            st.success(

                f"Your Score: {score}/{len(quiz_questions)}"

            )



        st.markdown(

            '</div>',

            unsafe_allow_html=True

        )



    

    if st.sidebar.button("Logout"):



        st.session_state.logged_in = False



        st.rerun()