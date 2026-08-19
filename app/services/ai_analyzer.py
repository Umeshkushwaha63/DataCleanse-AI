import pandas as pd
import numpy as np

from app.services.llm import ask_llm


def analyze_dataset(df: pd.DataFrame) -> str:
    """
    Analyze a dataset and generate
    column-by-column AI cleaning recommendations.
    """

    # =====================================================
    # BASIC DATASET INFORMATION
    # =====================================================

    rows = len(df)
    columns = len(df.columns)

    # =====================================================
    # BUILD COLUMN INFORMATION
    # =====================================================

    column_information = []

    for column in df.columns:

        series = df[column]

        # Missing values
        missing_count = int(
            series.isna().sum()
        )

        missing_percentage = (
            round(
                (missing_count / rows) * 100,
                2
            )
            if rows > 0
            else 0
        )

        # Unique values
        unique_count = int(
            series.nunique(dropna=True)
        )

        # Data type
        data_type = str(
            series.dtype
        )

        # Sample values
        sample_values = (
            series
            .dropna()
            .astype(str)
            .head(5)
            .tolist()
        )

        # ---------------------------------------------
        # Numeric information
        # ---------------------------------------------

        numeric_information = ""

        if pd.api.types.is_numeric_dtype(series):

            numeric_series = series.dropna()

            if len(numeric_series) > 0:

                q1 = numeric_series.quantile(0.25)
                q3 = numeric_series.quantile(0.75)

                iqr = q3 - q1

                if iqr != 0:

                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr

                    outlier_count = int(
                        (
                            (numeric_series < lower)
                            |
                            (numeric_series > upper)
                        ).sum()
                    )

                else:

                    outlier_count = 0

                numeric_information = f"""
Minimum: {numeric_series.min()}
Maximum: {numeric_series.max()}
Mean: {round(numeric_series.mean(), 2)}
Median: {round(numeric_series.median(), 2)}
Potential outliers: {outlier_count}
"""

        # ---------------------------------------------
        # Text information
        # ---------------------------------------------

        text_information = ""

        if (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):

            text_series = (
                series
                .dropna()
                .astype(str)
            )

            whitespace_count = int(
                (
                    text_series
                    != text_series.str.strip()
                ).sum()
            )

            text_information = f"""
Whitespace issues: {whitespace_count}
"""

        # ---------------------------------------------
        # Add column information
        # ---------------------------------------------

        column_information.append(
            f"""
-----------------------------------------
COLUMN: {column}
-----------------------------------------

Data type:
{data_type}

Missing values:
{missing_count}

Missing percentage:
{missing_percentage}%

Unique values:
{unique_count}

Sample values:
{sample_values}

{numeric_information}

{text_information}
"""
        )

    summary = "\n".join(
        column_information
    )

    # =====================================================
    # DUPLICATES
    # =====================================================

    duplicate_count = int(
        df.duplicated().sum()
    )

    duplicate_percentage = (
        round(
            (duplicate_count / rows) * 100,
            2
        )
        if rows > 0
        else 0
    )

    # =====================================================
    # DATASET MEMORY INFORMATION
    # =====================================================

    memory_usage = round(
        df.memory_usage(
            deep=True
        ).sum() / (1024 ** 2),
        2
    )

    # =====================================================
    # AI PROMPT
    # =====================================================

    prompt = f"""
You are an expert Data Analyst,
Data Quality Engineer, and AI Data Cleaning Assistant.

Your job is to analyze a dataset and provide
specific, safe, actionable cleaning recommendations.

IMPORTANT SAFETY RULE:

NEVER assume that data should automatically
be modified.

Important changes must always require
user approval.

=================================================
DATASET INFORMATION
=================================================

Rows: {rows}

Columns: {columns}

Memory usage: {memory_usage} MB

Duplicate rows: {duplicate_count}

Duplicate percentage: {duplicate_percentage}%

=================================================
COLUMN INFORMATION
=================================================

{summary}

=================================================
YOUR TASK
=================================================

Analyze every important data-quality problem.

For each issue, provide:

1. COLUMN
   Name the exact column.

2. ISSUE
   Clearly explain what is wrong.

3. EVIDENCE
   Mention the number or percentage
   that supports your finding.

4. WHY IT MATTERS
   Explain the possible business or
   analytical impact.

5. RECOMMENDED ACTION
   Recommend the safest cleaning approach.

6. RISK LEVEL
   Choose one:

   LOW
   MEDIUM
   HIGH

7. USER APPROVAL
   Say:

   REQUIRED

   for important changes.

=================================================
IMPORTANT RULES
=================================================

Do NOT recommend deleting important data
without explaining the risk.

Do NOT automatically fill missing values
without explaining why the selected method
is appropriate.

For numerical missing values, consider:
- median
- mean
- model-based imputation

For categorical missing values, consider:
- mode
- "Unknown"
- leaving the value missing

For duplicates:
- recommend removal only when duplicates
  are clearly unintended.

For outliers:
- DO NOT automatically delete them.
- Recommend investigation first.

For inconsistent categories:
- suggest standardization.

For whitespace:
- suggest trimming.

For incorrect data types:
- suggest conversion only when
  the conversion is safe.

=================================================
RESPONSE FORMAT
=================================================

Use this exact structure:

# AI DATA QUALITY REPORT

## 🔴 HIGH PRIORITY ISSUES

List serious problems here.

For each issue:

### Column: <column name>

**Issue:** ...

**Evidence:** ...

**Why it matters:** ...

**Recommended action:** ...

**Risk:** HIGH

**User approval:** REQUIRED


## 🟠 MEDIUM PRIORITY ISSUES

Use the same format.


## 🟢 LOW PRIORITY ISSUES

Use the same format.


## 📊 DATASET SUMMARY

Provide:

- Rows
- Columns
- Duplicate rows
- Major problems detected
- Overall data quality assessment


## 🤖 OVERALL RECOMMENDATION

Give a short practical cleaning strategy.

Remember:

The AI only recommends actions.

The user must approve important
changes before the dataset is modified.
"""

    # =====================================================
    # CALL LLM
    # =====================================================

    result = ask_llm(prompt)

    return result