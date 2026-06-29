import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import joblib


def main():
    # Load dataset
    df = pd.read_csv('.ipynb_checkpoints/Crop_recommendation.csv')

    # Feature columns and target label
    feature_columns = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[feature_columns]
    y = df['label']

    # Encode the crop labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    # Train random forest classifier
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Model accuracy: {accuracy:.4f}')

    # Save trained model and label encoder
    joblib.dump(model, 'crop_model.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    print('Saved crop_model.pkl and label_encoder.pkl')


if __name__ == '__main__':
    main()
