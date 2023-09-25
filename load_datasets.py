from pandas import read_json
from bz2 import open as bz2_uncompresser

with bz2_uncompresser("events.jsonl.bz2", 'rt', encoding='utf-8') as file:
    print("2214324")
    df_eidu_data = read_json(file, lines=True)

print(df_eidu_data.shape)