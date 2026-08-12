import os
import pandas as pd
import streamlit as st
import json
import plotly.graph_objects as go
from CDPpy_agent.agent.agent import CDPpy_agent
from CDPpy_agent.tools.data_handler import initialize_fed_batch_parameters, process_cell_line_data, export_data_to_excel
from CDPpy_agent.tools.plots import get_VCD_profile
from pydantic_ai import ModelResponse, ToolCallPart

INPUT_FOLDER = "input_files"
os.makedirs(INPUT_FOLDER, exist_ok=True)
OUTPUT_FOLDER = "output_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def agent_chat():
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
    if "fed_batch_param" not in st.session_state:
        st.session_state.fed_batch_param = None

    # Render existing conversation history
    for msg in st.session_state.display_history:
        with st.chat_message(msg["role"]):
            if "content" in msg:
                st.markdown(msg["content"])
            if "chart_json" in msg:
                st.plotly_chart(
                    msg["chart_json"],
                    use_container_width=True
                )

    if "latest_excel_filename" not in st.session_state:
        st.session_state.latest_excel_filename = None

    chat_with_agent()
    sidebar_menu()

def chat_with_agent():
    if user_input := st.chat_input("Ask me anything about your cell culture data..."):
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.display_history.append({
            "role": "user",
            "content": user_input
        })

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):

                current_deps = {
                    "params": st.session_state.get("fed_batch_param"),
                    "file_name": st.session_state.get("file_name"),
                    "local_file_path": st.session_state.get("local_file_path"),
                    "fed_batch_obj": st.session_state.get("fed_batch_obj"),
                    "latest_excel_filename": st.session_state.get("latest_excel_filename"),
                }

                try:
                    result = CDPpy_agent.run_sync(
                        user_input,
                        deps=current_deps,
                        message_history=(
                            st.session_state.message_history
                            if st.session_state.message_history
                            else None
                        )
                    )

                    # PydanticAI conversation history
                    st.session_state.message_history = result.all_messages()
                    response_text = result.output

                    # # Find Plotly figure returned by a tool
                    # plotly_fig = None

                    # for message in result.new_messages():
                    #     for part in message.parts:
                    #         if (
                    #             hasattr(part, "content")
                    #             and isinstance(part.content, str)
                    #             and part.content.startswith("PLOTLY_JSON:")
                    #         ):
                    #             json_str = part.content.removeprefix(
                    #                 "PLOTLY_JSON:"
                    #             )
                    #             plotly_fig = go.Figure(
                    #                 json.loads(json_str)
                    #             )

                    # # Display chart
                    # if plotly_fig is not None:
                    #     st.plotly_chart(
                    #         plotly_fig,
                    #         use_container_width=True
                    #     )
                    #     history_payload["chart_json"] = plotly_fig

                    # Display text
                    st.markdown(response_text)

                    # Store everything belonging to this response
                    history_payload = {
                        "role": "assistant",
                        "content": response_text,
                    }

                    st.session_state.display_history.append(
                        history_payload
                    )

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

        if uploaded_file is not None:
            st.session_state.uploaded_file = uploaded_file

        template_path = "input_files/Package_input_Template.xlsx"

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
                # Store dataframe under distinct session key to avoid overwriting file object
                df = pd.read_excel(uploaded_file)
                st.success(f"Successfully loaded: {uploaded_file.name}")
                st.dataframe(df.head(5))
                st.session_state.data_df = df

                local_file_path = os.path.join(INPUT_FOLDER, uploaded_file.name)
                with open(local_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.local_file_path = local_file_path
                st.session_state.file_name = uploaded_file.name
        
            except Exception as e:
                st.error(f"Error reading/saving file: {e}")
        
        st.subheader("Exports")
        show_output_files()

def show_output_files():
    folder_path = OUTPUT_FOLDER
    files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]
    
    if not files:
        st.info("No compiled reports found. Ask the agent to export your data!")
        return

    st.write(f"**Available Reports ({len(files)}):**")
    
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, "rb") as file_data:
                file_bytes = file_data.read()
            
            col_download, col_delete = st.columns([3, 1])

            with col_download:
                st.download_button(
                    label=f"Download {filename}",
                    data=file_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key=f"dl_btn_{filename}"
                )

            with col_delete:
                if st.button("🗑️", key=f"del_btn_{filename}", use_container_width=True, help=f"Delete {filename}"):
                    os.remove(file_path)
                    st.toast(f"Deleted {filename} successfully!")
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading {filename}: {e}")