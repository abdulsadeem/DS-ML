import pandas as pd
from reporter import DataReporter  # assuming this code is saved as reporter.py

# Load your dataset
df = pd.read_csv("data/customer_analytics.csv")

# Generate the report
DataReporter.generate_report(df)