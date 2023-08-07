from flask import Flask, render_template, request
from transformers import RobertaForSequenceClassification, AutoTokenizer
import torch
import np
from text_preprocessing import process_text
app = Flask(__name__)

model_2 = RobertaForSequenceClassification.from_pretrained("saved_weight")
tokenizer = AutoTokenizer.from_pretrained("wonrax/phobert-base-vietnamese-sentiment", use_fast=False)

def predict_sentiment(text):
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors='pt')
    outputs = model_2(**inputs)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    predictions = predictions.cpu().detach().numpy()
    return predictions[0]

def calculate_emotion_percentages(predictions):
    total_predictions = predictions.sum()
    percentages = (predictions / total_predictions) * 100
    return percentages

def map_position_to_label(position):
    label_mapping = {
        0: "Other",
        1: "Disgust",
        2: "Enjoyment",
        3: "Anger",
        4: "Surprise",
        5: "Sadness",
        6: "Fear"
        # Add more mappings as needed
    }
    return label_mapping.get(position, "Unknown")


@app.route('/', methods=['GET', 'POST'])
def index():
    input_text = None
    preprocessed_text = None
    predicted_label = None
    formatted_percentages = None

    if request.method == 'POST':
        input_text = request.form['text']
        if input_text:
            preprocessed_text = process_text(input_text)
            predictions = predict_sentiment(preprocessed_text)
            result_label = map_position_to_label(predictions.argmax())
            predicted_label = f"Predicted Emotion: {result_label}"
            
            emotion_percentages = calculate_emotion_percentages(predictions)  # Calculate emotion percentages

                        # Format the emotion percentages
            formatted_percentages = [f"{percentage:.3f}" for percentage in emotion_percentages]

    return render_template('index.html',input_text=input_text, preprocessed_text=preprocessed_text, predicted_label=predicted_label, emotion_percentages=formatted_percentages)
if __name__ == '__main__':
    app.run(debug=True)