import pandas as pd
from typing import List, Dict, Any, Optional

class ChartSelector:
    def select_chart_type(self, df: pd.DataFrame) -> str:
        """
        Determine the best chart type based on the dataframe structure.
        """
        if df.empty:
            return "none"

        num_cols = df.select_dtypes(include=['number']).columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        date_cols = df.select_dtypes(include=['datetime']).columns

        # Heuristics
        
        # Time Series: Date column + Numeric column
        if len(date_cols) >= 1 and len(num_cols) >= 1:
            return "line"
        
        # Comparison: 1 Categorical + 1 Numeric
        if len(cat_cols) == 1 and len(num_cols) == 1:
            # If few categories, maybe pie? But bar is safer.
            if df[cat_cols[0]].nunique() < 10:
                return "bar"
            return "bar"

        # Correlation: 2+ Numeric columns
        if len(num_cols) >= 2:
            return "scatter"

        # Composition: 1 Categorical + 1 Numeric (small number of categories)
        if len(cat_cols) == 1 and len(num_cols) == 1 and df[cat_cols[0]].nunique() <= 5:
            return "pie"

        # Default to table if no clear pattern
        return "table"
