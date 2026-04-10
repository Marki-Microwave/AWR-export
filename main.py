import MWO_Parser as MWO

parser = MWO.APFileParser()  # ← opens file dialog if no path given

df = parser.get_dataframe()
data_dict = parser.to_dict()

print(df.columns)
print("Original column for 'DB(|S(1,2)|)':", parser.get_original_column_name("DB(|S(1,2)|)"))
