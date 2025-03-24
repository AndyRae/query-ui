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

def calculate_odds_ratio(table: dict) -> str:
    try:
        numerator = table["exposed"]["with_outcome"] * table["unexposed"]["without_outcome"]
        denominator = table["exposed"]["without_outcome"] * table["unexposed"]["with_outcome"]
        
        if denominator == 0:
            return "Cannot calculate (division by zero)"
        
        odds_ratio = numerator / denominator
        return f"{odds_ratio:.2f}"
    except Exception as e:
        return f"Error calculating odds ratio: {str(e)}"

def main():
    st.title("OMOP Contingency Table Builder")
    
    # Sidebar for input parameters
    with st.sidebar:
        st.header("Query Parameters")
        
        # Exposure parameters
        st.subheader("Exposure")
        exposure_omop = st.text_input("Exposure OMOP Code", value="8507")
        exposure_table = st.selectbox(
            "Exposure Table",
            ["Condition", "Drug", "Procedure", "Measurement", "Observation"]
        )
        
        # Outcome parameters
        st.subheader("Outcome")
        outcome_omop = st.text_input("Outcome OMOP Code", value="24970")
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
                builder = ContingencyTableQuery(
                    exposure_omop_code=exposure_omop,
                    outcome_omop_code=outcome_omop,
                    exposure_table=exposure_table,
                    outcome_table=outcome_table
                )
                
                # Execute queries and get job responses
                with st.spinner("Executing queries..."):
                    table = builder.build_contingency_table(
                        client=client,
                        collection_id=settings.COLLECTION_ID,
                        owner="user1"
                    )
                
                # Display results
                st.header("Results")
                st.dataframe(table)
                
                # Calculate and display statistics
                st.subheader("Basic Statistics")
                total = sum(sum(cell for cell in row.values()) for row in table.values())
                st.write(f"Total number of patients: {total}")
                
                # Safer odds ratio calculation
                odds_ratio = calculate_odds_ratio(table)
                st.write(f"Odds Ratio: {odds_ratio}")
                
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