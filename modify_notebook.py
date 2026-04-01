import json
import os

notebook_path = os.path.join(os.path.dirname(__file__), 'idp.ipynb')

try:
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    updates = 0
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            source_lines = cell.get('source', [])
            new_source = []
            
            for line in source_lines:
                if 'pd.read_csv(\'C:/Users/cheta/Desktop/IDP-main/Reduced_Review_db.csv\')' in line:
                    # Found the line we want to replace
                    replacement = (
                        "# Fetch dataset from Firebase instead of local CSV\\n",
                        "import sys\\n",
                        "import os\\n",
                        "if os.path.abspath('.') not in sys.path: sys.path.append(os.path.abspath('.'))\\n",
                        "from firebase_manager import fetch_dataframe_from_firebase\\n",
                        "text = fetch_dataframe_from_firebase('reduced_reviews')"
                    )
                    # We convert to a list formatted the way ipynb expects
                    new_source.extend(replacement)
                    updates += 1
                else:
                    new_source.append(line)
                    
            cell['source'] = new_source
    
    if updates > 0:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1)
        print(f"Notebook modified successfully. Replaced {updates} instances.")
    else:
        print("No matching pd.read_csv lines found to replace.")
        
except Exception as e:
    print(f"Error modifying notebook: {e}")
