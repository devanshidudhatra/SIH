import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load pre-trained model and label encoder
model = joblib.load('network_rf_model.joblib')
label_encoder = joblib.load('network_label_encoder.joblib')

def predict_attack(file_path):
    # Load the new data
    new_data = pd.read_csv(file_path)
    
    # Remove unnecessary columns
    columns_to_remove = [
        'Unnamed: 0', 'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
        'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
        'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate', 'Label'
    ]
    
    new_data_cleaned = new_data.drop(columns=columns_to_remove, errors='ignore')

    # Perform prediction
    predictions = model.predict(new_data_cleaned)
    predicted_labels = label_encoder.inverse_transform(predictions)
    
    return predicted_labels[0]  # Return the prediction result (for the first entry)
