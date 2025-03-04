import streamlit as st
from contingency_table_builder import ContingencyTableQuery
from hutch_bunny.core.upstream.task_api_client import TaskApiClient
from hutch_bunny.core.settings import get_settings, DaemonSettings
import pandas as pd

def create_contingency_table(results: list) -> pd.DataFrame:
    """Creates a pandas DataFrame for the contingency table"""
    # Assuming results are in order: [11, 10, 01, 00]
    table_data = {
        'Outcome +': [results[0], results[2]],
        'Outcome -': [results[1], results[3]]
    }
    return pd.DataFrame(
        table_data,
        index=['Exposure +', 'Exposure -']
    )

def main():
    st.title("OMOP Contingency Table Builder")
    
    # Sidebar for input parameters
    with st.sidebar:
        st.header("Query Parameters")
        
        # Exposure parameters
        st.subheader("Exposure")
        exposure_omop = st.text_input("Exposure OMOP Code")
        exposure_table = st.selectbox(
            "Exposure Table",
            ["Condition", "Drug", "Procedure", "Measurement", "Observation"]
        )
        
        # Outcome parameters
        st.subheader("Outcome")
        outcome_omop = st.text_input("Outcome OMOP Code")
        outcome_table = st.selectbox(
            "Outcome Table",
            ["Condition", "Drug", "Procedure", "Measurement", "Observation"]
        )
        
        # Query button
        if st.button("Run Query"):
            if not exposure_omop or not outcome_omop:
                st.error("Please provide both OMOP codes")
                return
                
            try:
                # Initialize settings and client
                settings: DaemonSettings = get_settings(daemon=True)
                client = TaskApiClient(settings)
                
                # Create and execute query
                contingency_builder = ContingencyTableQuery(
                    exposure_omop_code=exposure_omop,
                    outcome_omop_code=outcome_omop,
                    exposure_table=exposure_table,
                    outcome_table=outcome_table
                )
                
                # Execute queries and get job responses
                with st.spinner("Executing queries..."):
                    job_responses = contingency_builder.execute_queries(
                        client=client,
                        collection_id=settings.COLLECTION_ID,
                        owner="user1"
                    )
                
                # Wait for jobs to complete
                with st.spinner("Waiting for results..."):
                    completed_jobs = contingency_builder.wait_for_jobs(client, job_responses)
                
                # Fetch results
                with st.spinner("Fetching results..."):
                    results = contingency_builder.fetch_results(client, completed_jobs)
                
                # Create and display contingency table
                contingency_table = create_contingency_table(results)
                
                # Display results
                st.header("Results")
                st.dataframe(contingency_table)
                
                # Add some basic statistics
                st.subheader("Basic Statistics")
                total = contingency_table.sum().sum()
                st.write(f"Total number of patients: {total}")
                
                # Calculate odds ratio
                odds_ratio = (contingency_table.iloc[0,0] * contingency_table.iloc[1,1]) / \
                           (contingency_table.iloc[0,1] * contingency_table.iloc[1,0])
                st.write(f"Odds Ratio: {odds_ratio:.2f}")
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Main content area
    st.markdown("""
    ### Instructions
    1. Enter the OMOP codes for your exposure and outcome variables
    2. Select the appropriate tables for each variable
    3. Click "Run Query" to generate the contingency table
    
    ### Example OMOP Codes
    - Diabetes mellitus: 201820
    - Heart disease: 316139
    - Male: 8507
    - Female: 8532
    """)

if __name__ == "__main__":
    main() 