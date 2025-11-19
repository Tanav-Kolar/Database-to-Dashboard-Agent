import streamlit as st
import asyncio
import pandas as pd
import sys
import os

# Add the project root to the python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent.sql_agent import SQLAgent
from src.visualisation.chart_selector import ChartSelector
from src.visualisation.plotly_generator import PlotlyGenerator
from dotenv import load_dotenv

# Load env vars
load_dotenv()

st.set_page_config(page_title="AI SQL Dashboard", page_icon="📊", layout="wide")

def main():
    st.title("📊 AI Database-to-Dashboard Agent")
    st.markdown("Ask questions about your data in plain English.")

    # Sidebar Config
    with st.sidebar:
        st.header("Configuration")
        st.subheader("Database")
        db_name = st.text_input("DB Name", value=os.getenv("DB_NAME", "postgres"))
        db_user = st.text_input("User", value=os.getenv("DB_USER", "postgres"))
        # Update env vars for the session (Agent uses os.getenv)
        if db_name: os.environ["DB_NAME"] = db_name
        if db_user: os.environ["DB_USER"] = db_user
        
        st.subheader("LLM")
        model = st.selectbox("Model", ["llama3", "llama2", "mistral", "codellama"], index=0)
        os.environ["OLLAMA_MODEL"] = model

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat Interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sql" in message:
                with st.expander("View SQL"):
                    st.code(message["sql"], language="sql")
            if "chart" in message:
                st.plotly_chart(message["chart"], use_container_width=True)
            if "data" in message:
                with st.expander("View Raw Data"):
                    st.dataframe(message["data"])

    if prompt := st.chat_input("What would you like to know?"):
        # User Message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                agent = SQLAgent()
                # Run async agent in sync streamlit
                response = asyncio.run(agent.process_query(prompt))

                if "error" in response:
                    st.error(response["error"])
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {response['error']}"})
                else:
                    # Success
                    sql = response["sql"]
                    data = response["results"]
                    
                    st.success("Query executed successfully!")
                    with st.expander("View SQL"):
                        st.code(sql, language="sql")

                    if data:
                        df = pd.DataFrame(data)
                        
                        # Visualization
                        selector = ChartSelector()
                        chart_type = selector.select_chart_type(df)
                        
                        generator = PlotlyGenerator()
                        fig = generator.generate_chart(df, chart_type)
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        with st.expander("View Raw Data"):
                            st.dataframe(df)

                        # Save to history
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "Here is the data you requested.",
                            "sql": sql,
                            "chart": fig,
                            "data": df
                        })
                    else:
                        st.info("Query returned no results.")
                        st.session_state.messages.append({"role": "assistant", "content": "Query returned no results.", "sql": sql})

if __name__ == "__main__":
    main()
