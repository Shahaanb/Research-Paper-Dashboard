# Research Paper Insights Dashboard
# Run with: streamlit run app.py

import numpy as np
import re
import os
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
import json
import pandas as pd
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Research Paper Insights Dashboard",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4F46E5;
        color: white;
    }
    .stButton>button:hover {
        background-color: #4338CA;
        color: white;
    }
    .insight-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)


#Extract text from uploaded PDF files
def get_text_from_pdf(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        try:
            pdf_reader = PdfReader(pdf)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            st.error(f"Error reading PDF {pdf.name}: {str(e)}")
    return text

#Split document into sections based on common research paper headers
def get_sections(docs):
    section_titles = [
        "abstract", "introduction", "background", "related work",
        "methodology", "methods", "approach", "experimental setup",
        "results", "findings", "evaluation", "experiments",
        "discussion", "limitations", "analysis",
        "conclusion", "conclusions", "future work", "future directions"
    ]
    
    #Create regex pattern
    pattern = r"(?i)\b(" + "|".join(section_titles) + r")\b"
    splits = re.split(pattern, docs)
    
    sections = {}
    current_section = "unknown"
    
    for i, part in enumerate(splits):
        part_clean = part.strip()
        if part_clean.lower() in section_titles:
            current_section = part_clean.lower()
            sections[current_section] = ""
        elif part_clean:
            if current_section in sections:
                sections[current_section] += " " + part_clean
            else:
                sections[current_section] = part_clean
    
    return sections

#Extract structured insights using OpenAI API
def extract_insights(sections, api_key):
    prompt = f'''
Extract structured insights from the following research paper sections.
Return JSON with these exact keys: summary, problem, methodology, findings, limitations, future_work.

Abstract: {sections.get('abstract', 'N/A')}
Introduction: {sections.get('introduction', 'N/A')}
Background: {sections.get('background', 'N/A')}
Methodology: {sections.get('methodology', sections.get('methods', 'N/A'))}
Results: {sections.get('results', sections.get('findings', 'N/A'))}
Discussion: {sections.get('discussion', 'N/A')}
Conclusion: {sections.get('conclusion', sections.get('conclusions', 'N/A'))}
Future Work: {sections.get('future work', sections.get('future directions', 'N/A'))}

Return your answer ONLY as valid JSON with no additional text or markdown formatting.
'''

    try:
        # Clean the API key before using
        clean_api_key = api_key.strip().strip('"').strip("'")
        
        client = OpenAI(api_key=clean_api_key)
        
        # FIXED: Correct API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a research paper analyzer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content
        
        # Clean up the response
        cleaned = re.sub(r"^```(json)?", "", response_text)
        cleaned = re.sub(r"```$", "", cleaned).strip()
        
        # Parse JSON
        insights = json.loads(cleaned)
        
        # Validate required keys
        required_keys = ["summary", "problem", "methodology", "findings", "limitations", "future_work"]
        for key in required_keys:
            if key not in insights:
                insights[key] = "Not available"
        
        return insights
        
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON parsing failed: {e}")
        return {
            "summary": "Error parsing response",
            "problem": "",
            "methodology": "",
            "findings": "",
            "limitations": "",
            "future_work": ""
        }
    except Exception as e:
        st.error(f"❌ API call failed: {e}")
        return None

#Save insights to CSV file
def save_insights(insights_list, filename="insights.csv"):
    try:
        df = pd.DataFrame(insights_list)
        df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        df.to_csv(filename, index=False)
        return df
    except Exception as e:
        st.error(f"Error saving insights: {e}")
        return None

#Display a styled insight card
def display_insight_card(title, content, icon):
    # FIX APPLIED HERE: Added style="color: #1f2937;" to the h3 tag
    st.markdown(f"""
        <div class="insight-card">
            <h3 style="color: #1f2937; margin-top: 0;">{icon} {title}</h3>
            <p style="color: #4B5563; line-height: 1.6;">{content}</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    #Title and description
    st.title("📄 Research Paper Insights Dashboard")
    st.markdown("**Extract and analyze key insights from academic research papers using AI**")
    st.markdown("---")
    
    #Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input with environment variable support
        default_api_key = os.getenv("OPENAI_API_KEY", "")
        # Debug: Show key info (first/last 4 chars only for security)
        if default_api_key:
            key_preview = f"{default_api_key[:7]}...{default_api_key[-4:]}"
            st.success(f"✅ API Key loaded from .env")
            st.text(f"Key preview: {key_preview}")
            st.text(f"Key length: {len(default_api_key)} chars")
                        
            api_key = default_api_key.strip() # Clean the key
            
            show_key_input = st.checkbox("Override with different key", value=False)
            if show_key_input:
                api_key = st.text_input(
                    "OpenAI API Key", 
                    type="password",
                    help="Enter your OpenAI API key to process papers"
                )
        else:
            st.warning("⚠️ No API key found in .env file")
            api_key = st.text_input(
                "OpenAI API Key", 
                type="password",
                help="Enter your OpenAI API key or set OPENAI_API_KEY in .env file"
            )
            if not api_key:
                st.info("💡 Tip: Create a .env file with OPENAI_API_KEY=your-key-here")
        
        st.markdown("---")
        
        #Sample data option
        st.header("Quick Start")
        use_sample = st.checkbox("Use Sample Data", help="Load a sample research paper for testing")
        
        st.markdown("---")
        st.markdown("### How to Use")
        st.markdown("""
        1. Enter your OpenAI API key
        2. Upload PDF files or use sample data
        3. Click 'Process Papers'
        4. View extracted insights
        5. Download results as CSV
        """)
    
    # Main content area
    if use_sample:
        st.info("Using sample research paper data")
        sample_text = """ABSTRACT
This paper explores the impact of AI on education. We highlight the main problem of scaling personalized learning.

INTRODUCTION
Artificial Intelligence has shown promise in adaptive tutoring systems. However, adoption is still limited due to infrastructure and training requirements.

METHODOLOGY
We conducted a mixed-methods study using surveys (N=300) and classroom experiments (n=25) across 5 different schools.

RESULTS
Our experiments show a 15% improvement in test scores when using AI-assisted tutoring. Student engagement increased by 22%.

DISCUSSION
While results are promising, some students reported reduced motivation due to automation. Teacher training is essential for success.

CONCLUSION
AI can enhance education, but more longitudinal studies are needed to understand long-term effects.

FUTURE WORK
We propose exploring the role of AI in collaborative learning environments and investigating socioeconomic impacts.
"""
        uploaded_files = None
        raw_text = sample_text
    else:
        # File uploader
        st.header("Upload Research Papers")
        uploaded_files = st.file_uploader(
            "Upload PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Select one or more PDF research papers"
        )
        raw_text = None
    
    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        process_button = st.button("🚀 Process Papers", use_container_width=True)
    
    # Processing logic
    if process_button:
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar")
            return
        
        if not use_sample and not uploaded_files:
            st.error("Please upload at least one PDF file or use sample data")
            return
        
        with st.spinner("Processing papers... This may take a minute."):
            try:
                # Extract text
                if not use_sample:
                    raw_text = get_text_from_pdf(uploaded_files)
                
                if not raw_text or len(raw_text.strip()) < 100:
                    st.error("Could not extract sufficient text from the document(s)")
                    return
                
                # Extract sections
                sections = get_sections(raw_text)
                
                # Extract insights
                insights = extract_insights(sections, api_key)
                
                if insights:
                    # Store in session state
                    st.session_state['insights'] = insights
                    st.session_state['sections'] = sections
                    st.success("Processing complete!")
                else:
                    st.error("Failed to extract insights")
                    
            except Exception as e:
                st.error(f"Error during processing: {e}")
    
    # Display results
    if 'insights' in st.session_state:
        insights = st.session_state['insights']
        
        st.markdown("---")
        st.header("Extracted Insights")
        
        # Summary section (full width)
        st.markdown("### Summary")
        display_insight_card("Executive Summary", insights.get('summary', 'N/A'), "📄")
        
        # Two column layout for other insights
        col1, col2 = st.columns(2)
        
        with col1:
            display_insight_card("Research Problem", insights.get('problem', 'N/A'), "🎯")
            display_insight_card("Key Findings", insights.get('findings', 'N/A'), "✅")
            display_insight_card("Future Work", insights.get('future_work', 'N/A'), "🔮")
        
        with col2:
            display_insight_card("Methodology", insights.get('methodology', 'N/A'), "🔬")
            display_insight_card("Limitations", insights.get('limitations', 'N/A'), "⚠️")
        
        # Download section
        st.markdown("---")
        st.header("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            df = pd.DataFrame([insights])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"research_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # JSON download
            json_str = json.dumps(insights, indent=2)
            st.download_button(
                label="📥 Download as JSON",
                data=json_str,
                file_name=f"research_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )


if __name__ == "__main__":
    main()