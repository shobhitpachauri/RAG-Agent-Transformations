import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class SnowflakeETL:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        self.cursor = self.conn.cursor()

    def load_data(self, file_path):
        """Load data from Excel file and transform it"""
        try:
            logger.info(f"Loading data from {file_path}")
            df = pd.read_excel(file_path)
            
            # Generate UUIDs for new records
            df['PROJECT_ID'] = [str(uuid.uuid4()) for _ in range(len(df))]
            
            # Transform data according to schema
            projects_df = self._transform_projects(df)
            budget_df = self._transform_budget(df)
            risks_df = self._transform_risks(df)
            milestones_df = self._transform_milestones(df)
            delays_df = self._transform_delays(df)
            
            # Load data into Snowflake
            self._load_to_snowflake('PROJECTS', projects_df)
            self._load_to_snowflake('PROJECT_BUDGET', budget_df)
            self._load_to_snowflake('PROJECT_RISKS', risks_df)
            self._load_to_snowflake('PROJECT_MILESTONES', milestones_df)
            self._load_to_snowflake('PROJECT_DELAYS', delays_df)
            
            logger.info("Data loading completed successfully")
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def _transform_projects(self, df):
        """Transform data for projects table"""
        return df[[
            'PROJECT_ID', 'PROJECT_NAME', 'PROJECT_TYPE',
            'START_DATE', 'PLANNED_END_DATE', 'ACTUAL_END_DATE',
            'STATUS', 'PRIORITY', 'OWNER'
        ]].copy()

    def _transform_budget(self, df):
        """Transform data for budget table"""
        budget_df = df[['PROJECT_ID', 'PLANNED_BUDGET', 'ACTUAL_BUDGET']].copy()
        budget_df['BUDGET_ID'] = [str(uuid.uuid4()) for _ in range(len(budget_df))]
        budget_df['CURRENCY'] = 'USD'
        budget_df['BUDGET_STATUS'] = budget_df.apply(
            lambda x: 'OVER_BUDGET' if x['ACTUAL_BUDGET'] > x['PLANNED_BUDGET'] else 'UNDER_BUDGET',
            axis=1
        )
        return budget_df

    def _transform_risks(self, df):
        """Transform data for risks table"""
        risks_df = df[['PROJECT_ID', 'RISK_TYPE', 'RISK_DESCRIPTION', 
                      'SEVERITY', 'PROBABILITY', 'MITIGATION_PLAN']].copy()
        risks_df['RISK_ID'] = [str(uuid.uuid4()) for _ in range(len(risks_df))]
        risks_df['STATUS'] = 'ACTIVE'
        return risks_df

    def _transform_milestones(self, df):
        """Transform data for milestones table"""
        milestones_df = df[['PROJECT_ID', 'MILESTONE_NAME', 
                           'PLANNED_DATE', 'ACTUAL_DATE']].copy()
        milestones_df['MILESTONE_ID'] = [str(uuid.uuid4()) for _ in range(len(milestones_df))]
        milestones_df['STATUS'] = milestones_df.apply(
            lambda x: 'COMPLETED' if pd.notnull(x['ACTUAL_DATE']) else 'IN_PROGRESS',
            axis=1
        )
        return milestones_df

    def _transform_delays(self, df):
        """Transform data for delays table"""
        delays_df = df[['PROJECT_ID', 'MILESTONE_ID', 'DELAY_REASON']].copy()
        delays_df['DELAY_ID'] = [str(uuid.uuid4()) for _ in range(len(delays_df))]
        delays_df['DELAY_DAYS'] = df['DELAY_DAYS']
        delays_df['IMPACT_LEVEL'] = df['IMPACT_LEVEL']
        return delays_df

    def _load_to_snowflake(self, table_name, df):
        """Load DataFrame to Snowflake table"""
        try:
            logger.info(f"Loading data to {table_name}")
            success, nchunks, nrows, _ = write_pandas(
                self.conn,
                df,
                table_name,
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA')
            )
            logger.info(f"Loaded {nrows} rows to {table_name}")
        except Exception as e:
            logger.error(f"Error loading data to {table_name}: {str(e)}")
            raise

    def close(self):
        """Close Snowflake connection"""
        self.cursor.close()
        self.conn.close()

def main():
    etl = SnowflakeETL()
    try:
        # Load data from Excel file
        etl.load_data('data.xlsx')
    finally:
        etl.close()

if __name__ == "__main__":
    main() 