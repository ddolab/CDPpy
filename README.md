# CDPpy

CDPpy (Cell-culture Data Pipeline Python package) is an open-source library designed to analyze fed-batch cell culture data from multiple experiments and cell lines. The package features the functions of a data processing pipeline and visualization toolbox. The processing pipeline reads raw data from Excel files following a fixed template, derives variables such as cumulative substrate consumption and various specific rates, and exports the processed dataset into an Excel file. The particular rates show changing cellular activities in culture over time, providing process optimization insights. The visualization toolbox enables users to analyze process profiles across experimental runs and cell lines, aiding in future experimental design. In this repository, we include the source code for the package, an instruction for package setup, and a Jupyter notebook that provides step-by-step guidelines for data processing and visualization using an example dataset.

UPDATE (7/13/26): Early stages of LLM agent construction! Try it [here](https://cdppy-agent.streamlit.app/).

## Citation
DOI: https://doi.org/10.13020/7bwf-a974 (link will be active soon)

URL: https://hdl.handle.net/11299/264596

### Developer

- Yen-An Lu (lu000285@umn.edu), Department of Chemical Engineering and Materials Science, University of Minnesota
- Yudai Fukae (fukae001@umn.edu), Department of Biomedical Engineering, University of Minnesota
- Prof. Wei-Shou Hu, Department of Chemical Engineering and Materials Science, University of Minnesota
- Prof. Qi Zhang, Department of Chemical Engineering and Materials Science, University of Minnesota

## Requirements/Package setup

Dependecies can be found in 'requirements.txt' file.

To recreate in conda environments:

'''conda create --name cdppy
conda activate cdppy
pip install -r requirements.txt
'''

## Input Excel template

The package reads the data from Excel files following a fixed template. One can find the template in the `input_files` folder.

## Tutorial

The Jupyter notebook `Package_tutorial.ipynb` provides a tutorial designed for running on Google Colab. 

A PDF instruction on executing the notebook on Google Colab can be found in `Tutorial_Jupyter_notebook_instruction.pdf`.


