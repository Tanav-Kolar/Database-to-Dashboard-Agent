import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Any

class PlotlyGenerator:
    def generate_chart(self, df: pd.DataFrame, chart_type: str) -> Any:
        """Generate a Plotly figure based on the chart type."""
        
        if chart_type == "bar":
            # Assume first categorical is x, first numeric is y
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            if len(cat_cols) > 0 and len(num_cols) > 0:
                return px.bar(df, x=cat_cols[0], y=num_cols[0], title=f"{num_cols[0]} by {cat_cols[0]}")
        
        elif chart_type == "line":
            # Assume first date/cat is x, first numeric is y
            date_cols = df.select_dtypes(include=['datetime']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            x_col = date_cols[0] if len(date_cols) > 0 else df.columns[0]
            if len(num_cols) > 0:
                return px.line(df, x=x_col, y=num_cols[0], title=f"{num_cols[0]} over Time")

        elif chart_type == "scatter":
            num_cols = df.select_dtypes(include=['number']).columns
            if len(num_cols) >= 2:
                return px.scatter(df, x=num_cols[0], y=num_cols[1], title=f"{num_cols[1]} vs {num_cols[0]}")

        elif chart_type == "pie":
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            num_cols = df.select_dtypes(include=['number']).columns
            if len(cat_cols) > 0 and len(num_cols) > 0:
                return px.pie(df, names=cat_cols[0], values=num_cols[0], title=f"Distribution of {num_cols[0]}")

        # Default/Table
        return go.Figure(data=[go.Table(
            header=dict(values=list(df.columns), fill_color='paleturquoise', align='left'),
            cells=dict(values=[df[col] for col in df.columns], fill_color='lavender', align='left')
        )])
