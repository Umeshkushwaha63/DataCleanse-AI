from app.services.llm import ask_llm


def generate_cleaning_recommendation(
    column: str,
    dtype: str,
    missing_count: int,
    unique_values: int,
    total_rows: int,
) -> str:
    """
    Generate an AI recommendation for cleaning a dataset column.

    The AI only recommends a cleaning method.
    It never modifies the dataset automatically.
    """

    prompt = f"""
You are a senior data quality expert.

Analyze the following dataset column:

Column: {column}
Data type: {dtype}
Missing values: {missing_count}
Unique values: {unique_values}
Total rows: {total_rows}

Recommend the safest cleaning method.

Rules:
1. Never modify the data automatically.
2. Recommend only ONE cleaning method.
3. Consider the data type.
4. Consider the number of missing values.
5. Give a short and practical reason.
6. Confidence must be between 0 and 100%.

Allowed methods:
- Mean
- Median
- Mode
- Forward Fill
- Backward Fill
- Custom Value
- Leave Missing

Return exactly:

Method: <method>
Reason: <short reason>
Confidence: <0-100>%
"""

    try:
        return ask_llm(prompt)

    except Exception as exc:
        return (
            "Method: Leave Missing\n"
            f"Reason: AI recommendation failed: {exc}\n"
            "Confidence: 0%"
        )