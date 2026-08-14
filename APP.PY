import streamlit as st
from openai import OpenAI

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(page_title="IB-TechPrep", page_icon="📈", layout="wide")

# 2. Sidebar Navigation (How users move around the app)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Dashboard", "AI Tutor", "Quiz Engine", "The Vault"])

# 3. Screen 1: Main Dashboard UI
if page == "Dashboard":
    st.title("🎓 Welcome to IB-TechPrep")
    st.subheader("Your AI-Powered PGDM Launchpad")
    st.divider()

    # Goal Selection
    st.markdown("### 🎯 What are you preparing for today?")
    col1, col2 = st.columns(2)
    
    with col1:
        track = st.selectbox("Select Track", ["Investment Banking (NISM)", "Data Analytics (Microsoft/Alteryx)"])
    
    with col2:
        if track == "Investment Banking (NISM)":
            cert = st.selectbox("Select Certification", ["NISM I - Currency", "NISM VIII - Equity Derivatives", "NISM XV - Research Analyst"])
        else:
            cert = st.selectbox("Select Certification", ["MO-200 Excel Specialist", "PL-300 Power BI", "Alteryx Designer Core"])

    st.divider()

    # Mock Progress Tracker
    st.markdown(f"### 📊 Readiness for {cert}")
    st.progress(45) 
    st.caption("Complete more mock quizzes to increase your readiness score.")

# 4. Screen 2: The AI Tutor (Powered by Groq)
elif page == "AI Tutor":
    st.title("🤖 The AI Interview Tutor")
    st.write("Ask me anything about Investment Banking or Data Analytics.")

    # Securely ask for the Groq API Key
    api_key = st.sidebar.text_input("Enter your Groq API Key (starts with gsk_):", type="password")
    st.sidebar.caption("Get one at [console.groq.com/keys](https://console.groq.com/keys)")

    # Create a split-screen layout: Chat (Left) and Scratchpad (Right)
    chat_col, scratch_col = st.columns([2, 1])

    with chat_col:
        # Initialize the chat memory
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I am your IB & Analytics tutor. Do you want to practice for a NISM interview, or write some Python code?"}
            ]

        # Display all previous chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # The input box where the student types
        if prompt := st.chat_input("E.g., Explain the Capital Asset Pricing Model (CAPM)..."):
            
            # Show the user's message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            if not api_key:
                st.error("⚠️ Please enter your Groq API Key in the sidebar first.")
            else:
                try:
                    with st.spinner("Thinking like a Wall Street Analyst..."):
                        # Initialize OpenAI Client (Pointing to Groq's servers)
                        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                        
                        # Instructions telling the AI how to act
                        system_instruction = """
                        You are an expert Investment Banking and Data Analytics tutor. 
                        You are helping a PGDM student prepare for NISM and Microsoft certifications.
                        Keep answers highly professional, accurate, and easy to read.
                        Whenever relevant, provide SQL, Python, or Excel formulas to bridge finance and tech.
                        """
                        
                        # Prepare messages array for the API
                        openai_messages = [{"role": "system", "content": system_instruction}]
                        for msg in st.session_state.messages:
                            openai_messages.append({"role": msg["role"], "content": msg["content"]})
                        
                        # Call the Groq API!
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=openai_messages
                        )
                        
                        bot_reply = response.choices[0].message.content
                        
                        # Show the AI's response
                        with st.chat_message("assistant"):
                            st.markdown(bot_reply)
                        
                        # Save the AI's response to memory
                        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                        
                except Exception as e:
                    st.error(f"API Error: {e}")

    with scratch_col:
        st.markdown("### 📝 Code & Formula Scratchpad")
        st.info("When the AI generates SQL, Python, or Excel macros in the chat, you can easily copy the logic here.")
        
        # Static placeholders for now
        st.code("SELECT asset_name, SUM(amount) \nFROM portfolio \nGROUP BY asset_name;", language="sql")
        st.code("=NPV(rate, value1, [value2], ...)", language="excel")

# 5. Screen 3: The Quiz Engine
elif page == "Quiz Engine":
    st.title("📝 Certification Quiz Engine")
    st.write("Test your knowledge with real SEBI/Microsoft mock questions.")
    st.divider()

    # 1. Setup the Database (We will hardcode two NISM questions for the MVP)
    mock_db = [
        {
            "question": "The purchase of a share in one market and the simultaneous sale in a different market to benefit from price differentials is known as:",
            "options": ["Speculation", "Hedging", "Arbitrage", "Mortgage"],
            "answer": "Arbitrage",
            "explanation": "Arbitrage is a riskless trade that profits by exploiting the price differences of identical financial instruments on different markets."
        },
        {
            "question": "The buyer of an Option cannot lose more than the option premium paid.",
            "options": ["True only for European options", "True only for American options", "True for all options", "False for all options"],
            "answer": "True for all options",
            "explanation": "The buyer of an option (both Call and Put) has limited risk. The maximum loss is strictly restricted to the premium paid upfront."
        }
    ]

    # 2. Setup Session State (Short-term memory to track scores and questions)
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "quiz_done" not in st.session_state:
        st.session_state.quiz_done = False
    if "show_explanation" not in st.session_state:
        st.session_state.show_explanation = False

    # 3. The Quiz UI
    if not st.session_state.quiz_done:
        q = mock_db[st.session_state.q_index]
        
        st.markdown(f"### Question {st.session_state.q_index + 1} of {len(mock_db)}")
        st.markdown(f"**{q['question']}**")
        
        # User makes a choice
        user_choice = st.radio("Select an answer:", q["options"], index=None, key=f"radio_{st.session_state.q_index}")
        
        # Submit Logic
        if not st.session_state.show_explanation:
            if st.button("Submit Answer"):
                if user_choice:
                    st.session_state.show_explanation = True
                    if user_choice == q["answer"]:
                        st.session_state.score += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Please select an answer first.")
        
        # Feedback Logic
        if st.session_state.show_explanation:
            if user_choice == q["answer"]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The right answer is: **{q['answer']}**")
            
            st.info(f"💡 **Explanation:** {q['explanation']}")
            
            # Move to next question or finish
            if st.button("Next"):
                st.session_state.show_explanation = False
                if st.session_state.q_index < len(mock_db) - 1:
                    st.session_state.q_index += 1
                else:
                    st.session_state.quiz_done = True
                st.rerun()
                
    # 4. The Final Score Screen
    else:
        st.balloons()
        st.markdown("## 🎉 Mock Test Complete!")
        st.metric(label="Your Final Score", value=f"{st.session_state.score} / {len(mock_db)}")
        
        if st.button("Retake Quiz"):
            st.session_state.score = 0
            st.session_state.q_index = 0
            st.session_state.quiz_done = False
            st.session_state.show_explanation = False
            st.rerun()

# 5. Screen 3: The Quiz Engine
elif page == "Quiz Engine":
    st.title("📝 Certification Quiz Engine")
    st.write("Test your knowledge with real SEBI/Microsoft mock questions.")
    st.divider()

    # 1. Setup the Database (We will hardcode two NISM questions for the MVP)
    mock_db = [
        {
            "question": "The purchase of a share in one market and the simultaneous sale in a different market to benefit from price differentials is known as:",
            "options": ["Speculation", "Hedging", "Arbitrage", "Mortgage"],
            "answer": "Arbitrage",
            "explanation": "Arbitrage is a riskless trade that profits by exploiting the price differences of identical financial instruments on different markets."
        },
        {
            "question": "The buyer of an Option cannot lose more than the option premium paid.",
            "options": ["True only for European options", "True only for American options", "True for all options", "False for all options"],
            "answer": "True for all options",
            "explanation": "The buyer of an option (both Call and Put) has limited risk. The maximum loss is strictly restricted to the premium paid upfront."
        }
    ]

    # 2. Setup Session State (Short-term memory to track scores and questions)
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "quiz_done" not in st.session_state:
        st.session_state.quiz_done = False
    if "show_explanation" not in st.session_state:
        st.session_state.show_explanation = False

    # 3. The Quiz UI
    if not st.session_state.quiz_done:
        q = mock_db[st.session_state.q_index]
        
        st.markdown(f"### Question {st.session_state.q_index + 1} of {len(mock_db)}")
        st.markdown(f"**{q['question']}**")
        
        # User makes a choice
        user_choice = st.radio("Select an answer:", q["options"], index=None, key=f"radio_{st.session_state.q_index}")
        
        # Submit Logic
        if not st.session_state.show_explanation:
            if st.button("Submit Answer"):
                if user_choice:
                    st.session_state.show_explanation = True
                    if user_choice == q["answer"]:
                        st.session_state.score += 1
                    st.rerun()
                else:
                    st.warning("⚠️ Please select an answer first.")
        
        # Feedback Logic
        if st.session_state.show_explanation:
            if user_choice == q["answer"]:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. The right answer is: **{q['answer']}**")
            
            st.info(f"💡 **Explanation:** {q['explanation']}")
            
            # Move to next question or finish
            if st.button("Next"):
                st.session_state.show_explanation = False
                if st.session_state.q_index < len(mock_db) - 1:
                    st.session_state.q_index += 1
                else:
                    st.session_state.quiz_done = True
                st.rerun()
                
    # 4. The Final Score Screen
    else:
        st.balloons()
        st.markdown("## 🎉 Mock Test Complete!")
        st.metric(label="Your Final Score", value=f"{st.session_state.score} / {len(mock_db)}")
        
        if st.button("Retake Quiz"):
            st.session_state.score = 0
            st.session_state.q_index = 0
            st.session_state.quiz_done = False
            st.session_state.show_explanation = False
            st.rerun()

# 6. Screen 4: The Vault
elif page == "The Vault":
    st.title("📂 The Cheat Sheet Vault")
    st.write("Your quick-reference library for exams and technical interviews.")
    st.divider()

    # Create 3 tabs for different categories
    tab1, tab2, tab3 = st.tabs(["📊 Finance Formulas", "💻 Python & SQL", "📉 Excel & DAX"])

    with tab1:
        st.subheader("Capital Asset Pricing Model (CAPM)")
        st.info("Expected Return = Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)")
        st.markdown("**Use Case:** Calculating the expected return on an asset based on its systematic risk.")
        
        st.subheader("Weighted Average Cost of Capital (WACC)")
        st.info("WACC = (Equity / Total Value) * Cost of Equity + (Debt / Total Value) * Cost of Debt * (1 - Tax Rate)")
        st.markdown("**Use Case:** Finding the discount rate used in DCF modeling to value a company.")

    with tab2:
        st.subheader("Essential SQL for Analytics")
        st.code("""-- Find the top 5 highest valued portfolios
SELECT client_name, SUM(asset_value) as total_value
FROM portfolios
GROUP BY client_name
ORDER BY total_value DESC
LIMIT 5;""", language="sql")
        
        st.subheader("Python: Pandas Data Manipulation")
        st.code("""import pandas as pd

# Calculate rolling 30-day moving average for a stock
df['30_Day_MA'] = df['Closing_Price'].rolling(window=30).mean()

# Calculate daily returns
df['Daily_Return'] = df['Closing_Price'].pct_change()""", language="python")

    with tab3:
        st.subheader("Power BI: DAX Time Intelligence")
        st.code("""-- Calculate Year-to-Date (YTD) Revenue
YTD_Revenue = TOTALYTD(SUM(Sales[Revenue]), 'Date'[Date])

-- Calculate Year-over-Year (YoY) Growth
YoY_Growth = 
  DIVIDE(
    [Total Revenue] - CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date])),
    CALCULATE([Total Revenue], SAMEPERIODLASTYEAR('Date'[Date]))
  )""", language="dax")