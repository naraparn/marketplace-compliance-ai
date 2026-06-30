import streamlit as st
from openai import OpenAI
from pydantic import BaseModel, Field
import pypdf
import os

# Initialize OpenAI (Automatically uses your Streamlit Secret key)
# Make sure your secret in Streamlit Cloud is named OPENAI_API_KEY
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class ComplianceAudit(BaseModel):
    triage_status: str = Field(description="Strictly output 'PASS' or 'FAIL'")
    confidence_score: int = Field(description="Confidence in extraction from 1 to 100")
    recycled_content_detected: str = Field(description="E.g., '100% Recycled Aluminum' or 'None detected'")
    critical_errors: list[str] = Field(description="List of specific anomalies like expired dates or missing signatures.")
    executive_summary: str = Field(description="1-sentence operational summary.")
    audit_trail_quote: str = Field(description="Exact string match from the PDF proving the claim.")

st.set_page_config(page_title="AI Automation Copilot", layout="wide")
st.title("⚡ AI Automation: Claims Verification Engine")

with st.sidebar:
    st.header("Stage Supplier Document")
    # Added 'accept_multiple_files=False' and explicit PDF type
    uploaded_file = st.file_uploader("Upload Supplier PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        # Improved PDF reading logic with error handling
        with st.spinner("Extracting text from PDF..."):
            pdf_reader = pypdf.PdfReader(uploaded_file)
            document_text = ""
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    document_text += text + "\n"
        
        if not document_text.strip():
            st.error("The PDF appears to be empty or an image-only scan. Please use a text-based PDF.")
        else:
            st.success(f"File successfully parsed: **{uploaded_file.name}**")

            if st.button("Run AI Automation Audit", type="primary"):
                with st.spinner("Executing layout extraction and baseline matching via OpenAI..."):
                    prompt = f"""
                    You are a rigorous Apple PACE Regulatory Compliance Auditor.
                    Review this document text against hardware safety standards.
                    Rules for failing a document:
                    1. If the issuance date is older than 3 years from today (2026).
                    2. If an authorized signature is marked blank or missing.
                    Extract the schema precisely.
                    
                    DOCUMENT TEXT:
                    {document_text}
                    """
                    
                    response = client.beta.chat.completions.parse(
                        model="gpt-4o-2024-08-06",
                        messages=[
                            {"role": "system", "content": "You are a precise regulatory compliance auditor."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format=ComplianceAudit,
                        temperature=0.0
                    )
                    
                    data = response.choices[0].message.parsed
                    c1, c2, c3 = st.columns(3)
                    status = data.triage_status
                    
                    c1.metric("Verification Status", f"{status} {'✅' if status=='PASS' else '❌'}")
                    c2.metric("Extraction Confidence", f"{data.confidence_score}%")
                    c3.metric("Recycled Content", data.recycled_content_detected)
                    
                    st.divider()
                    st.subheader("Operational Triage Summary")
                    st.write(data.executive_summary)
                    
                    if data.critical_errors and status == "FAIL":
                        st.error("**Audit Blockers Identified:**")
                        for e in data.critical_errors:
                            st.markdown(f"- {e}")
                            
                    with st.expander("🔍 Verify Source Citation (Audit Trail)"):
                        st.code(data.audit_trail_quote)
                        
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    st.info("Please upload a PDF file to begin the audit.")