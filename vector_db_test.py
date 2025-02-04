# -*- coding: utf-8 -*-
"""AP1-test2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BR-geh5qRdcWcDCz5EZtsZwaMB0LDty1
"""

!pip install langchain langchain-community sentence-transformers lancedb tantivy==0.20.1

data_path = "/content/drive/MyDrive/ap1_data/"

import pandas as pd

df = pd.read_csv(data_path + "annotations_1645.csv")

df.head()

from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
import lancedb

db = lancedb.connect("/tmp/db")
model = get_registry().get("sentence-transformers").create()

class Schema(LanceModel):
    topic: str
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()

table = db.create_table("comments", schema=Schema, mode="overwrite")

for idx,row in df.iterrows():
  # table.add([{"topic":row["Topic"],"text":row["Comments"],"vector":model.compute_source_embeddings(row["Comments"])[0]}])
  table.add([{"topic":row["Topic"],"text":row["Comments"]}])

table.create_fts_index("text")

"""Vector search"""

sample_comment = "Russia is relentless. I feel sorry for the Ukrainian civilians who are caught in this nasty game."

table.search(sample_comment,query_type="vector").metric('dot').limit(10).to_pandas()

"""BM25 text search"""

table.search(sample_comment,query_type="fts").limit(10).to_pandas()

"""hybrid"""

from lancedb.rerankers import RRFReranker
reranker = RRFReranker()
table.search(sample_comment,query_type="hybrid").rerank(reranker=reranker).limit(10).to_pandas()