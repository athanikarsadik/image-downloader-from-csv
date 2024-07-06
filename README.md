# Image Background Remover

This Python script automates the process of removing backgrounds from images listed in a CSV file and then zipping the processed images.

## Requirements:

- Python 3.7 or higher

## Setup:

1. **Install Python:** Download and install the latest version of Python from [https://www.python.org/](https://www.python.org/) if you don't already have it.

2. **Create Virtual Environment (Recommended):**

   - Open your terminal or command prompt.
   - Navigate to the project directory where you saved the script.
   - Create a virtual environment (using `venv` or your preferred method):
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - Windows:
       ```bash
       venv\Scripts\activate
       ```
     - macOS/Linux:
       ```bash
       source venv/bin/activate
       ```

3. **Install Dependencies:**
   - Run the following command to install the required libraries:
     ```bash
     pip install -r requirements.txt
     ```

## Usage:

1. **Add input.csv:**

   - Place your **input.csv** file containing image URLs in the `data` folder.
   - Each URL should be separated by a semicolon (`;`) if there are multiple URLs in a cell.

2. **Run the Script:**
   - Open your terminal or command prompt.
   - Navigate to the project directory.
   - Run the script using the following command:
     ```bash
     python main.py
     ```

## Output:

- Processed images will be saved in the `output/images` folder.
- A zip file named `processed_images.zip` containing all the processed images will be created in the `output` folder.

## Notes:

- Make sure your CSV file is named **input.csv** and is placed in the correct directory.
- The script will automatically create the `output` and `output/images` folders if they don't exist.
- You can customize the output directory names by modifying the variables at the beginning of the `main.py` script if needed.
