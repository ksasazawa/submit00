import pandas as pd

df = pd.read_csv("test6.csv", header=None, names=["ASIN"])

print(df)