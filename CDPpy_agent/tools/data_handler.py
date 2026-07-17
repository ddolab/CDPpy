from pydantic_ai import RunContext
from CDPpy_agent.agent.agent import CDPpy_agent
from CDPpy import FedBatchCellCulture, FedBatchParameters
from CDPpy.helper import input_path
import tempfile
import streamlit as st
import os
# from io import BytesIO

OUTPUT_FOLDER = "output_files"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@CDPpy_agent.tool
def initialize_fed_batch_parameters(
    ctx: RunContext[tuple], # Handled by Pydantic AI,
    cell_line_name: str,
    use_concentration_after_feed: bool = False,
    use_feed_concentration: bool = True
) -> str:
    """Initialize the FedBatchParameters configuration structure. This tool MUST be called to configure parameters before running cell culture data analysis pipelines.

    Args:
        cell_line_name (str): The name of the cell line. Must match the Excel file input exactly.
        use_concentration_after_feed (bool): True if measurements are taken after feeding.
        use_feed_concentration (bool): True if the feeding composition is known.
    """
    try:
        param_obj = FedBatchParameters(
            cell_line_name=cell_line_name,
            use_concentration_after_feed=use_concentration_after_feed,
            use_feed_concentration=use_feed_concentration
        )
        
        # 2. Store it directly into Streamlit's Session State so your app UI can access it globally
        st.session_state.fed_batch_param = param_obj
        
        return f"Successfully initialized parameters for cell line '{cell_line_name}'."
    except Exception as e:
        return f"Error initializing parameters: {str(e)}"

@CDPpy_agent.tool
def process_cell_line_data(
    ctx: RunContext[tuple], # Handled by Pydantic AI
) -> str:
    """Run the complete data processing pipeline for the configured cell line.

    This tool loads the uploaded dataset and processes it using the parameters 
    configured in the initialization step.
    """
    print("Starting data processing...")
    # print(st.session_state.keys())
    # print(st.session_state.get("uploaded_file"))
    if "fed_batch_param" not in st.session_state or st.session_state.fed_batch_param is None:
        return (
            "ERROR: Cannot process data because FedBatchParameters are not initialized. "
            "You must ask the user for their Cell Line Name, post-feed measurements status, "
            "and feeding composition availability. Once they provide it, call `initialize_fed_batch_parameters` first."
        )

    # data_file = BytesIO(ctx.deps["file_bytes"])  # temp_file_path = st.session_state.get("temp_file_path") # If using Option 2 (Disk Path)

    # If no file is detected in session state
    # if data_file is None: #and temp_file_path is None:
    #     return (
    #         "ERROR: No file has been uploaded yet. Please instruct the user to "
    #         "upload their Excel or CSV data file in the sidebar before we can proceed."
    #    )

    try:
        # Instantiate the processing object
        CL_fed_batch = FedBatchCellCulture()
        fed_batch_param = st.session_state.fed_batch_param
        path = input_path(ctx.deps["file_name"])  # Use the filename from session state for loading
        CL_fed_batch.load_data(file=ctx.deps["local_file_path"])  # Use the filename from session state for loading
        # source_name = data_file.name
            
        # Or use the stored temp file path if your library strictly needs a string path (Option 2)
        # elif temp_file_path is not None:
        #     CL_fed_batch.load_data(file=temp_file_path)
        #     source_name = st.session_state.get("uploaded_filename", "temp_file")

        # Perform the actual package data processing
        CL_fed_batch.perform_data_process(parameters=[fed_batch_param])
        
        # Save the processed object back into state so the "Save/Download" tool can find it
        st.session_state.fed_batch_obj = CL_fed_batch

        return (
            f"Successfully loaded and processed '{ctx.deps['file_name']}' "
            f"for cell line '{fed_batch_param.cell_line_name}'."
        )

    except Exception as e:
        return f"Error during data processing: {str(e)}"
    
@CDPpy_agent.tool
def export_data_to_excel(
    ctx: RunContext[tuple],
    output_filename: str = "processed_data_export.xlsx"
) -> str:
    """Save the processed cell culture data results to an Excel spreadsheet.

    This tool should be run AFTER data processing is complete to generate a 
    downloadable Excel report of the results.

    Args:
        output_filename: The desired name for the generated Excel file. Defaults to 'processed_data_export.xlsx'.
    """
    # 1. Check if the cell line has been processed first
    # (We assume 'CL_fed_batch' holds the instantiated and processed FedBatchCellCulture object)
    print("Exporting data to Excel...")
    try:
        CL_fed_batch = st.session_state.get("fed_batch_obj")
    except Exception as e:
        return f"Error accessing processed cell line object: {str(e)}"

    if CL_fed_batch is None:
        # make sure in your actual code you store the real instantiated object in st.session_state.fed_batch_obj!
        return (
            "Error: Cell line has not been processed yet. "
            "Please run the data processing pipeline first using `process_cell_line_data`."
        )

    try:
        if not output_filename.endswith(".xlsx"):
            output_filename += ".xlsx"

        # Save the processed data to an Excel file in memory
        CL_fed_batch.save_excel(file_name=output_filename)

        local_file_path = os.path.join(OUTPUT_FOLDER, output_filename)
        with open(local_file_path, "rb") as f:
            excel_bytes = f.read()

        # st.session_state.latest_excel = excel_bytes  # Store the Excel bytes for download
        st.session_state.latest_excel_filename = output_filename

        return (
            f"Successfully saved and compiled the processed data into '{output_filename}'. "
            "The file is now ready. You can download it directly from the sidebar!"
        )

    except Exception as e:
        return f"Error saving cell line to Excel: {str(e)}"