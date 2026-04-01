import os
from firebase_manager import upload_csv_to_firebase

if __name__ == "__main__":
    # We will upload the smaller dataset. The same can be done for Review_db.csv if needed.
    csv_file = os.path.join(os.path.dirname(__file__), 'Reduced_Review_db.csv')
    
    if not os.path.exists(csv_file):
        print(f"Error: Could not find {csv_file}")
    else:
        print(f"Uploading {csv_file} to Firebase. This may take a moment depending on internet speed...")
        upload_csv_to_firebase(csv_file, 'reduced_reviews')
        print("Upload complete! You can now run your Jupyter Notebook.")
