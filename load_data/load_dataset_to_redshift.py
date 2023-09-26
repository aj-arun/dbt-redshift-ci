from pandas import read_json
from sqlalchemy import create_engine
from bz2 import open as bz2_uncompresser

import os
print(os.getcwd())
print(os.listdir())
print(os.listdir("../"))

with bz2_uncompresser("transform_data/events.jsonl.bz2", 'rt', encoding='utf-8') as file:
    df_eidu_data = read_json(file, lines=True)

print(df_eidu_data.shape)
