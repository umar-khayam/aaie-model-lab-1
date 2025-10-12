from sklearn.preprocessing import LabelEncoder
import pandas as pd

class DatasetHandler:
    def __init__(self, dataset: pd.DataFrame, model_type: str):
        self.dataset = dataset
        self.model_type = model_type
        self.validate_dataset()

    def validate_dataset(self):
        if self.model_type == "ai_detection":
            required = {"text", "labels", "predictions"}
        elif self.model_type == "feedback_generation":
            required = {"text", "generated_texts"}
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

        missing = [k for k in required if k not in self.dataset.columns]
        if missing:
            raise ValueError(f"Dataset missing required fields: {missing}")

    def encode_labels(self, col: str):
        """Encode string labels to integers if needed."""
        try:
            int_labels = [int(x) for x in self.dataset[col]]
            label_names = sorted(set(int_labels))
        except ValueError:
            le = LabelEncoder()
            encoded_labels = le.fit_transform(self.dataset[col])
            int_labels = encoded_labels
            label_names = sorted(set(encoded_labels))
        return int_labels, label_names

    def iter_classification(self):
        for _, row in self.dataset.iterrows():
            yield row['text'], row['labels'], row['predictions']

    def iter_generative(self):
        for _, row in self.dataset.iterrows():
            yield row['text'], row['generated_texts']

    def iter_rows(self):
        """Yield each row as a dict."""
        for _, row in self.dataset.iterrows():
            yield row.to_dict()