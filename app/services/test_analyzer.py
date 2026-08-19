import pandas as pd

from app.services.ai_analyzer import analyze_dataset


# Create a small test dataset

df = pd.DataFrame({
    "Name": [
        "A",
        "B",
        "C",
        None,
        "E"
    ],

    "Age": [
        20,
        21,
        None,
        23,
        24
    ],

    "Salary": [
        30000,
        35000,
        40000,
        None,
        50000
    ]
})


result = analyze_dataset(df)


print("\n")
print("=" * 60)
print("AI DATA QUALITY ANALYSIS")
print("=" * 60)
print("\n")

print(result)

print("\n")
print("=" * 60)