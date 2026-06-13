import streamlit as st
import openai
import pandas as pd
from datetime import datetime

# 1. Page Config (Wide layout for a dashboard feel)
st.set_page_config(page_title="AI-Driven Seller Risk & Compliance Platform", layout="wide")

# 2. Sidebar Configuration
with st.sidebar:
    st.header("⚙️ System Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.markdown("---")
    st.subheader("Current Policy Guardrails")
    st.info("1. Expiration date must be after Dec 2026.\n2. Heavy metal (Lead) < 90 ppm.\n3. Laboratory must be accredited (e.g., SGS, Intertek).")

# 3. Dashboard Header
st.title("📊 AI-Driven Marketplace Risk & Compliance Platform")
st.markdown("Automated LLM decisioning engine for seller qualification and risk mitigation.")

# 4. Executive Metrics (Mock data to show scale)
st.subheader("Real-Time Operational Metrics (Last 30 Days)")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Total Applications Processed", value="26,402", delta="+1,204")
col2.metric(label="Average Approval Latency", value="1.2 sec", delta="-47.9 hrs")
col3.metric(label="Current Pass Rate", value="84.2%", delta="-1.1%")
col4.metric(label="Manual Hours Saved", value="14,200 hrs", delta="+800 hrs")

st.markdown("---")

# 5. Batch Processing Interface
st.subheader("📥 Process New Seller & Vendor Documents")
st.markdown("Upload compliance documents for immediate AI evaluation.")

# We use .txt files here so it's incredibly fast and doesn't require complex PDF libraries
uploaded_files = st.file_uploader("Drop .txt compliance reports here", type=["txt"], accept_multiple_files=True)

if st.button("Run Batch AI Audit"):
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
    elif not uploaded_files:
        st.warning("⚠️ Please upload at least one .txt file.")
    else:
        st.write("### 🧠 Live AI Audit Results")
        
        new_audit_results = []
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            for file in uploaded_files:
                # Read the text file
                document_text = file.read().decode("utf-8")
                
                with st.spinner(f"Analyzing {file.name}..."):
                    # System prompt forcing the AI to evaluate based on rules
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are an automated risk compliance engine. Evaluate the provided document text strictly against these rules: 1. Expiration > Dec 2026. 2. Lead < 90 ppm. 3. Accredited lab. Output a final decision starting with exactly 'APPROVED' or 'REJECTED', followed by a short explanation."},
                            {"role": "user", "content": document_text}
                        ]
                    )
                    
                    ai_output = response.choices[0].message.content
                    decision = "REJECTED" if "REJECTED" in ai_output.upper() else "APPROVED"
                    
                    # Display the result in a clean dropdown expander
                    with st.expander(f"Result for {file.name} - {decision}"):
                        if decision == "APPROVED":
                            st.success(ai_output)
                        else:
                            st.error(ai_output)
                            
                    # Save data to build our live table
                    new_audit_results.append({
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Vendor File": file.name,
                        "AI Decision": decision,
                        "Processing Time": "1.1s"
                    })
                    
            st.success(f"Successfully processed {len(uploaded_files)} documents.")
            
            # Show the newly processed items in a dataframe table
            st.subheader("📑 Recent Batch Audit Log")
            df = pd.DataFrame(new_audit_results)
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error during AI execution: {e}")

# 6. Historical Data Table (Always visible to make it look like an active system)
st.markdown("---")
st.subheader("🗄️ Historical Audit Log")
historical_data = {
    "Seller / Vendor ID": ["SLR-8839", "VND-1022", "SLR-4491", "VND-9920", "SLR-3312"],
    "Entity Type": ["3rd Party Seller", "1st Party Vendor", "3rd Party Seller", "1st Party Vendor", "3rd Party Seller"],
    "Document Type": ["Certificate of Authenticity", "Lab Test Report", "Lab Test Report", "Safety Data Sheet", "Certificate of Authenticity"],
    "AI Decision": ["APPROVED", "REJECTED", "APPROVED", "APPROVED", "REJECTED"],
    "Flagged Reason": ["N/A", "Lead content > 90ppm", "N/A", "N/A", "Expired Lab Cert"],
    "Audit Date": ["2026-06-12", "2026-06-12", "2026-06-11", "2026-06-11", "2026-06-10"]
}
st.dataframe(pd.DataFrame(historical_data), use_container_width=True)