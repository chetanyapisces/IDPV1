import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import json

CREDENTIALS_FILE = 'firebase-credentials.json'

def _initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(CREDENTIALS_FILE)
            firebase_admin.initialize_app(cred)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find the Firebase credentials file at {CREDENTIALS_FILE}. Please download it from Firebase Console -> Project Settings -> Service Accounts, and save it in this directory.")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase: {e}")

def upload_csv_to_firebase(csv_path, collection_name='reduced_reviews'):
    """Reads a CSV file into a pandas dataframe and uploads it to Firebase Firestore in batches."""
    print("Initializing Firebase...")
    _initialize_firebase()
    db = firestore.client()
    
    print(f"Reading CSV from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    print("Converting DataFrame to JSON...")
    records = df.fillna("").to_dict(orient='records')
    
    print(f"Uploading {len(records)} to Firestore under collection '{collection_name}' in batches...")
    
    batch = db.batch()
    count = 0
    total = 0
    for record in records:
        doc_ref = db.collection(collection_name).document()
        # Firestore cannot serialize complex float NaN mappings or custom objects,
        # but `.fillna("")` on the dataframe ensures we have standard strings/numbers.
        batch.set(doc_ref, record)
        count += 1
        
        # Firestore batch supports up to 500 operations
        if count == 500:
            batch.commit()
            total += 500
            print(f"Committed {total} records...")
            batch = db.batch() # start a new batch
            count = 0
            
    if count > 0:
        batch.commit()
        total += count
        print(f"Committed {total} records...")
        
    print(f"Successfully uploaded {csv_path} to Firestore collection '{collection_name}'")

def fetch_dataframe_from_firebase(collection_name='reduced_reviews'):
    """Fetches data from Firebase Firestore and returns a pandas DataFrame."""
    print("Initializing Firebase...")
    _initialize_firebase()
    db = firestore.client()
    
    print(f"Fetching data from collection '{collection_name}'...")
    docs = db.collection(collection_name).stream()
    data = [doc.to_dict() for doc in docs]
    
    if data:
        print("Data fetched successfully! Converting to DataFrame...")
        return pd.DataFrame(data)
    else:
        print(f"No data found at collection '{collection_name}'. Are you sure you uploaded it?")
        return pd.DataFrame()
