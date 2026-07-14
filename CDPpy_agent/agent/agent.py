from pydantic_ai import Agent, RunContext, Tool
from CDPpy_agent.tools.data_handler import initialize_fed_batch_parameters, process_cell_line_data, export_data_to_excel
import asyncio
import streamlit as st
import pandas as pd 
import os
from dotenv import load_dotenv

# Load the API key from the .env file into your system environment variables
load_dotenv()

@st.cache_resource
def get_agent() -> Agent:
    """Initialize and return the PydanticAI Agent."""
    return Agent(
        'google:gemini-3.1-flash-lite',
        deps_type=[],
        tools=[initialize_fed_batch_parameters, process_cell_line_data, export_data_to_excel],
        system_prompt=(
            "You are a bioprocess data handler agent. Your primary role is to manage and process datasets for analysis. " \
            "When responding to requests, provide clear and concise replies.",            
            "You should ensure that the data is clean, well-structured, and ready for further analysis. " \
            "The data can be uploaded by the user on the left sidebar at any time." \
            "Ask the user to upload the necessary data files and provide clear instructions on how to do so. " \
            "You can not perform any analysis if the user does not provide the data, but you can explain the process. " \
            "After the user uploads the data, ask if it it a perfusion or fed-batch cell culture experiment. " \
            # "If the user does not provide the cell culture type, default to fed-batch. " \
            "If perfusion is selected, say that that functionality has not been implemented yet. " \
            "CRITICAL RULES: \n"
            "1. You CANNOT analyze or process fed-batch data unless the `FedBatchParameters` have been initialized first.\n"
            "2. If the user mentions 'fed-batch', 'process data', 'load excel', or starts a configuration, you MUST immediately check "
            "if parameters are set. If not, you MUST proactively ask the user for these 3 things:\n"
            "   - Cell Line Name (Must match their excel sheet exactly, e.g. 'CellLine1')\n"
            "   - Whether they have concentration measurements after feeding (Yes/No)\n"
            "   - Whether the feeding composition is known (Yes/No)\n"
            "3. Once you obtain this information, call the `initialize_fed_batch_parameters` tool immediately.\n"
            "4. Only after initialization is successful, proceed to call `process_cell_line_data`."
            "5. If the user asks to save the processed data, call the `export_data_to_excel` tool. Only do this if the data has been processed and is available in session state."
        ),
    )

def agent_loop():
    agent = get_agent()

    st.title("CDPpy Data Handler Agent")
    st.caption("This agent is responsible for preparing datasets for analysis, and producing plots and reports based on the processed data.")


    if "message_history" not in st.session_state:
        st.session_state.message_history = []

    if "display_history" not in st.session_state:
        st.session_state.display_history = []

    # Render existing conversation history
    for msg in st.session_state.display_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Track processed CSVs for download
    if "latest_csv" not in st.session_state:
        st.session_state.latest_csv = None
    if "latest_csv_filename" not in st.session_state:
        st.session_state.latest_csv_filename = "processed_data.csv"


    # 2. Sidebar for Uploads & Downloads
    with st.sidebar:
        st.header("Data files")
        
        uploaded_file = st.file_uploader(
            "Upload Cell Culture Data File", 
            type=["xlsx", "xls", "csv"],
            help="Upload your raw cell culture data here. Make sure that the format follows the template!.",
            key="uploaded_file_uploader"
        )

        # Preserve upload state explicitly so later tool calls can access the file.
        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file
        elif st.session_state.get("uploaded_file") is not None:
            uploaded_file = st.session_state.uploaded_file

        template_path = "input_files/Package_input_Template.xlsx"  # Relative to your Streamlit app root

        if os.path.exists(template_path):
            with open(template_path, "rb") as file:
                st.download_button(
                    label="Download Blank Excel Template",
                    data=file,
                    file_name="CDPpy_Template.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.error("Template file not found in repository!")
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                st.success(f"Successfully loaded: {uploaded_file.name}")
                st.dataframe(df.head(5)) # Quick preview
                st.session_state.uploaded_file = uploaded_file

                notification_text = f"[System Notification] The user has successfully uploaded a data file named '{uploaded_file.name}'."
        
                # If message history is empty, initialize it with this notification
                if not st.session_state.message_history:
                    st.session_state.message_history = []
                
                # Silently notify the message history that data is loaded
                if not any("[System Notification]" in str(m) for m in st.session_state.message_history):
                    st.info("Agent is now aware of your uploaded dataset.")
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        st.subheader("Exports")
        if st.session_state.get("latest_csv"):
            st.download_button(
                label="Download Processed CSV",
                data=st.session_state.latest_csv,
                file_name=st.session_state.latest_csv_filename,
                mime="text/csv",
                use_container_width=True
            )
        if "latest_excel" in st.session_state and st.session_state.latest_excel is not None:
            st.download_button(
                label="Download Processed Excel",
                data=st.session_state.latest_excel,
                file_name=st.session_state.latest_excel_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.info("No processed data available for download yet. Ask the agent to export the processed dataset!")

    if user_input := st.chat_input("Ask me anything about your cell culture data..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.display_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("CDPpy Agent"):
            with st.spinner("Thinking..."):
                # async def run_agent():
                current_deps = (
                    st.session_state.get("fed_batch_param"),
                )
                result = agent.run_sync(
                    user_input,
                    deps=current_deps,
                    message_history=st.session_state.message_history if st.session_state.message_history else None
                )
                
                try:
                    # result = asyncio.run(run_agent())
                    response_text = result.output
                    st.session_state.message_history = result.all_messages()               
                    st.markdown(response_text)
                    st.session_state.display_history.append({"role": "CDPpy Agent", "content": response_text})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
