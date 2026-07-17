from CDPpy_agent.tools.data_handler import initialize_fed_batch_parameters, process_cell_line_data, export_data_to_excel
from CDPpy_agent.agent.agent import CDPpy_agent
import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd

# Load the API key from the .env file into your system environment variables
load_dotenv()
INPUT_FOLDER = "input_files"
os.makedirs(INPUT_FOLDER, exist_ok=True)
OUTPUT_FOLDER = "output_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def agent_chat():
    agent = CDPpy_agent

    st.title("CDPpy Agent")
    st.caption("This agent can help with preparing cell culture datasets for analysis, and producing plots and reports based on the processed data.")


    if "message_history" not in st.session_state:
        st.session_state.message_history = []
    if "display_history" not in st.session_state:
        st.session_state.display_history = []

    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "file_name" not in st.session_state:
        st.session_state.file_name = None
    if "local_file_path" not in st.session_state:
        st.session_state.local_file_path = None
    if "fed_batch_obj" not in st.session_state:
        st.session_state.fed_batch_obj = None

    # Render existing conversation history
    for msg in st.session_state.display_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Track processed CSVs for download
    # if "latest_excel" not in st.session_state:
    #     st.session_state.latest_excel = None
    if "latest_excel_filename" not in st.session_state:
        st.session_state.latest_excel_filename = None

    chat_with_agent()
    sidebar_menu()  # Call the sidebar function to render the sidebar

def chat_with_agent():
    if user_input := st.chat_input("Ask me anything about your cell culture data..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.display_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("CDPpy Agent"):
            with st.spinner("Thinking..."):
                # async def run_agent():
                current_deps = {
                    "params": st.session_state.get("fed_batch_param"),
                    "file_name": st.session_state.get("file_name"),
                    "local_file_path": st.session_state.get("local_file_path"),
                    "fed_batch_obj": st.session_state.get("fed_batch_obj"),
                    # "latest_excel": st.session_state.get("latest_excel"),
                    "latest_excel_filename": st.session_state.get("latest_excel_filename"),
                }

                result = CDPpy_agent.run_sync(
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
                    # if st.session_state.get("latest_excel") is not None:
                    #     st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")


def sidebar_menu():
    with st.sidebar:
        st.header("Data files")
        
        uploaded_file = st.file_uploader(
            "Upload Cell Culture Data File", 
            type=["xlsx", "xls"],
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
                df = pd.read_excel(uploaded_file)
                st.success(f"Successfully loaded: {uploaded_file.name}")
                st.dataframe(df.head(5)) # Quick preview
                st.session_state.uploaded_file = df

                try:
                    local_file_path = os.path.join(INPUT_FOLDER, uploaded_file.name)
                    with open(local_file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.session_state.local_file_path = local_file_path
                    st.session_state.file_name = uploaded_file.name
                    notification_text = f"[System Notification] The user has successfully uploaded a data file named '{uploaded_file.name}'."
                except Exception as e:
                    st.error(f"Error saving uploaded file locally: {e}")
                    notification_text = f"[System Notification] The user attempted to upload a data file named '{uploaded_file.name}', but an error occurred while saving it locally: {e}"
        
                # If message history is empty, initialize it with this notification
                if not st.session_state.message_history:
                    st.session_state.message_history = []
                
                # Silently notify the message history that data is loaded
                if not any("[System Notification]" in str(m) for m in st.session_state.message_history):
                    st.info("Agent is now aware of your uploaded dataset.")
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        st.subheader("Exports")
        show_output_files()
        
def show_output_files():
    """Scans a local directory and displays downloable buttons for all Excel files."""
    folder_path = OUTPUT_FOLDER  # Directory where processed Excel files are stored
        
    # Get all files ending with .xlsx or .xls
    files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]
    
    if not files:
        st.info("No compiled reports found. Ask the agent to export your data!")
        return

    st.write(f"**Available Reports ({len(files)}):**")
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        try:
            # Read the file's binary data
            with open(file_path, "rb") as file_data:
                file_bytes = file_data.read()
            
            col_download, col_delete = st.columns([3, 1])

            # Render a custom download button for this specific file
            with col_download:
                st.download_button(
                    label=f"Download {filename}",
                    data=file_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"dl_btn_{filename}"  # Unique key for Streamlit state tracking
                )

            # Render delete button next to the download button
            with col_delete:
                # Use a trash/delete icon on the button
                if st.button("🗑️", key=f"del_btn_{filename}", use_container_width=True, help=f"Delete {filename}"):
                    # Remove the file from disk
                    os.remove(file_path)
                    st.toast(f"Deleted {filename} successfully!")
                    # Force Streamlit to rerun immediately so the deleted file vanishes from the UI
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading {filename}: {e}")