import joblib

model = joblib.load("internship_model.pkl")

text = [
    "Pay registration fee to confirm internship",
    "Python developer internship with interview"
]

predictions = model.predict(text)

for description, prediction in zip(text, predictions):
    print("Internship:", description)
    print("Prediction:", "Suspicious" if prediction == 1 else "Less Suspicious")
    print("--------------------")