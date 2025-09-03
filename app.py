#Imports
import numpy as np
import re
import os
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import json
import pandas as pd


def main():
    insights = extract_insights(get_sections("""ABSTRACT
This paper explores the impact of AI on education. We highlight the main problem of scaling personalized learning.

INTRODUCTION
Artificial Intelligence has shown promise in adaptive tutoring systems. However, adoption is still limited.

METHODOLOGY
We conducted a mixed-methods study using surveys (N=300) and classroom experiments (n=25).

RESULTS
Our experiments show a 15% improvement in test scores when using AI-assisted tutoring.

DISCUSSION
While results are promising, some students reported reduced motivation due to automation.

CONCLUSION
AI can enhance education, but more longitudinal studies are needed.

FUTURE WORK
We propose exploring the role of AI in collaborative learning environments.
"""))
    print(save_insights([insights]))




def get_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_sections(docs):
    section_titles = [
        "abstract", "introduction", "background",
        "methodology", "methods", "approach",
        "results", "findings", "evaluation",
        "discussion", "limitations",
        "conclusion", "future work"
    ]
    splits = re.split(r"(?i)\b(" + "|".join(section_titles) + r")\b",docs)
    sections = {}
    current_section = "unknown"
    
    for part in splits:
        part_clean = part.strip()
        if part_clean.lower() in section_titles:
            current_section = part_clean.lower()
            sections[current_section] = ""
        else:
            sections[current_section] = sections.get(current_section, "") + " " + part_clean
    
    return sections

def extract_insights(sections):
    prompt = f'''
    Extract structured insights from the following research paper sections.
    Return JSON with keys: summary, problem, methodology, findings, limitations, future_work.


    Abstract:    {sections.get('abstract', '')}
    Introduction: {sections.get('introduction', '')}
    Methodology: {sections.get('methodology', '')}
    Results:     {sections.get('results', '')}
    Discussion:  {sections.get('discussion', '')}
    Conclusion:  {sections.get('conclusion', '')}
    Future Work: {sections.get('future work', '')}

Return your answer ONLY as valid JSON.
Do not include explanations or extra text.
'''

    client = OpenAI()
    response = client.responses.create(
    model="gpt-4o",
    input=prompt)
    cleaned = re.sub(r"^```(json)?", "", response.output_text)
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed:", e)
        return {
            "problem": "",
            "methodology": "",
            "findings": "",
            "limitations": "",
            "future_work": ""
        }

def save_insights(insights_list, file="insights.csv"):
    df = pd.DataFrame(insights_list)
    df.to_csv(file, index=False)
    return df



if __name__ == "__main__":
    main()