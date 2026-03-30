RAGS PDF FILE READER
To start the application 
------
# 1. Make sure you're in the right directory
pwd  # Shows current path - should show something like /c/Users/.../Downloads/Rag_APp

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Git Bash specific)
source venv/Scripts/activate

# You should now see (venv) at the beginning of your prompt

# 4. Install requirements
pip install -r requirements.txt

# 5. Run the app
streamlit run run.py