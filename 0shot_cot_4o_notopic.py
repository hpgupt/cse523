# -*- coding: utf-8 -*-
"""AP1-0shot-CoT-4o-notopic.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19--KY25bvO-AhpSqFMAw6exnZaSjuCks
"""

!pip install langchain
!pip install -qU langchain-openai

import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

data_path = "/content/drive/MyDrive/ap_data/"

"""Youtube Data"""

df = pd.read_csv(data_path+"annotations_1645.csv")

df.head()

import getpass
import os
os.environ["OPENAI_API_KEY"] = getpass.getpass()

"""0 shot prompting gpt-40-mini"""

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0.3, max_tokens=500)

from typing import Optional
from langchain_core.pydantic_v1 import BaseModel, Field,constr

class ClassificationOutput(BaseModel):
    output: str
structured_llm = llm.with_structured_output(ClassificationOutput)

from langchain.prompts import ChatPromptTemplate
prompt_template = ChatPromptTemplate.from_template(
    """
    There are two pieces of information provided:
    Consider this comment left by a user on a youtube video: "{comment}"
    Whataboutism is the practice of deflecting criticism or avoiding an unfavorable issue by raising a different, more favorable matter, or by making a counter accusation.
    Identify whether the above comment exhibits whataboutism. Let's think step by step. Please output your answer at the end as ##<answer>". The answer should be either of two options: "whataboutism" or "not whataboutism".
    """
)

def classify_comment(row):
    prompt = prompt_template.format_messages(
        title=row['Title'],
        topic=row['Topic'],
        comment=row['Comments']
    )
    output = structured_llm.invoke(prompt)
    return output.output

from tqdm import tqdm
tqdm.pandas()
df['output'] = df.progress_apply(classify_comment, axis=1)

df.to_csv(data_path+"output_yt_0shot-cot-notopic.csv", index=False)

def map_output(output):
    if 'not' in output:
        return 0
    else:
        return 1
true_labels = list(df['Label'])
predicted_labels = list(df['output'].apply(map_output))

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

"""Twitter data"""

t_df = pd.read_csv(data_path+"twitter_data_1204.csv")

t_df.head()

prompt_template_tw = ChatPromptTemplate.from_template(
    """
    There are two pieces of information provided:
    This reply tweet left by a user on an another tweet: "{comment}"
    Whataboutism is the practice of deflecting criticism or avoiding an unfavorable issue by raising a different, more favorable matter, or by making a counter accusation.
    Identify whether the above reply tweet exhibits whataboutism. Let's think step by step. Please output your answer at the end as ##<answer>". The answer should be either of two options: "whataboutism" or "not whataboutism".
    """
)

def classify_tw(row):
    prompt = prompt_template_tw.format_messages(
        title=row['Title'],
        topic=row['Topic'],
        comment=row['Comments']
    )
    print (prompt)
    output = structured_llm.invoke(prompt)
    return output.output

from tqdm import tqdm
tqdm.pandas()
t_df['output'] = t_df.progress_apply(classify_tw, axis=1)

t_df.to_csv(data_path+"output_tw_0shot-cot-notopic.csv", index=False)

true_labels = list(t_df['Label'])
predicted_labels = list(t_df['output'].apply(map_output))

accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")

"""Analysis of 0 shot results"""

llm2 = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=10)

prompt_template_ans = ChatPromptTemplate.from_template(
    """
    Following piece of text is output of another AI model whose task was to figure out if a sentence exhibits whataboutism or not, determine what is the result saying and output only "whataboutism" or "not whataboutism" accordingly. If the result contains something irrelevant then output "none".
    Result: {output}
    """
)

class ClassificationOutputAns(BaseModel):
    output: constr(regex=r"^(whataboutism|not whataboutism|none)$")
structured_llm_ans = llm2.with_structured_output(ClassificationOutputAns)

result_df_yt = pd.read_csv(data_path+"output_yt_0shot-cot-notopic.csv")
result_df_tw  = pd.read_csv(data_path+"output_tw_0shot-cot-notopic.csv")

def map_output(output):
    if '##whataboutism' in output:
        return 1
    elif '##not' in output:
        return 0
    elif 'not whataboutism' in output:
        return 0
    else:
      prompt = prompt_template_ans.format_messages(
          output=output
      )
      out = structured_llm_ans.invoke(prompt).output
      if out == "whataboutism":
        return 1
      elif out == "not whataboutism":
        return 0
      else:
        return None

result_df_yt['output'] = result_df_yt['output'].apply(map_output)
result_df_tw['output'] = result_df_tw['output'].apply(map_output)

result_df_yt = result_df_yt.dropna(subset=['output'])
result_df_tw = result_df_tw.dropna(subset=['output'])
# result_df_tw = result_df_tw.dropna()
print (result_df_yt.shape)
print (result_df_tw.shape)
# print (result_df_tw.shape

predicted_labels_yt = list(result_df_yt['output'])
predicted_labels_tw = list(result_df_tw['output'])
actual_labels_yt = list(result_df_yt['Label'])
actual_labels_tw = list(result_df_tw['Label'])

from sklearn.metrics import precision_score, recall_score, f1_score

def calculate_classwise_metrics(actual_labels, predicted_labels, class_name):
    precision = precision_score(actual_labels, predicted_labels, pos_label=class_name)
    recall = recall_score(actual_labels, predicted_labels, pos_label=class_name)
    f1 = f1_score(actual_labels, predicted_labels, pos_label=class_name)
    return precision, recall, f1

print("YouTube Dataset:")
classes = [0, 1]
for cls in classes:
    cl = "W" if cls else "NW"
    precision, recall, f1 = calculate_classwise_metrics(actual_labels_yt, predicted_labels_yt, class_name=cls)
    print(f"Class {cl} - Precision: {precision:.2f}, Recall: {recall:.2f}, F1 Score: {f1:.2f}")

print("\nTwitter Dataset:")
for cls in classes:
    cl = "W" if cls else "NW"
    precision, recall, f1 = calculate_classwise_metrics(actual_labels_tw, predicted_labels_tw, class_name=cls)
    print(f"Class {cl} - Precision: {precision:.2f}, Recall: {recall:.2f}, F1 Score: {f1:.2f}")