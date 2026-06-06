import pandas as pd

df = pd.read_csv("DSL-StrongPasswordData.csv")

print("Shape:", df.shape)

print("\nColumn Names:")
print(df.columns.tolist())

print("\nDataset Info:")
print(df.info())

print("\nMissing Values:")
print(df.isnull().sum())