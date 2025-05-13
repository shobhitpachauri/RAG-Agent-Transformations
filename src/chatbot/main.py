import os
from typing import List, Dict
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
import snowflake.connector
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ProjectChatbot:
    def __init__(self):
        # Initialize Snowflake connection
        self.conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )

        # Initialize OpenAI
        self.llm = OpenAI(temperature=0.7)

        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Create prompt template
        self.prompt = PromptTemplate(
            input_variables=["chat_history", "human_input", "project_data"],
            template="""You are an AI assistant specialized in project risk assessment and management.
            Use the following project data to answer questions:
            
            Project Data:
            {project_data}
            
            Chat History:
            {chat_history}
            
            Human: {human_input}
            AI: """
        )

        # Create LLM chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=True
        )

    def get_project_data(self, project_id: str = None) -> Dict:
        """Fetch project data from Snowflake"""
        try:
            if project_id:
                query = """
                SELECT 
                    p.PROJECT_NAME,
                    p.PROJECT_TYPE,
                    p.STATUS,
                    p.PRIORITY,
                    pb.PLANNED_BUDGET,
                    pb.ACTUAL_BUDGET,
                    COUNT(pr.RISK_ID) as ACTIVE_RISKS,
                    COUNT(pd.DELAY_ID) as TOTAL_DELAYS
                FROM PROJECTS p
                LEFT JOIN PROJECT_BUDGET pb ON p.PROJECT_ID = pb.PROJECT_ID
                LEFT JOIN PROJECT_RISKS pr ON p.PROJECT_ID = pr.PROJECT_ID AND pr.STATUS = 'ACTIVE'
                LEFT JOIN PROJECT_DELAYS pd ON p.PROJECT_ID = pd.PROJECT_ID
                WHERE p.PROJECT_ID = %s
                GROUP BY 1, 2, 3, 4, 5, 6
                """
                cursor = self.conn.cursor()
                cursor.execute(query, (project_id,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        'project_name': result[0],
                        'project_type': result[1],
                        'status': result[2],
                        'priority': result[3],
                        'planned_budget': float(result[4]),
                        'actual_budget': float(result[5]),
                        'active_risks': result[6],
                        'total_delays': result[7]
                    }
            else:
                # Get summary of all projects
                query = """
                SELECT 
                    COUNT(*) as TOTAL_PROJECTS,
                    COUNT(CASE WHEN STATUS = 'ON_TRACK' THEN 1 END) as ON_TRACK,
                    COUNT(CASE WHEN STATUS = 'AT_RISK' THEN 1 END) as AT_RISK,
                    COUNT(CASE WHEN STATUS = 'DELAYED' THEN 1 END) as DELAYED,
                    AVG(CASE WHEN pb.ACTUAL_BUDGET > pb.PLANNED_BUDGET 
                        THEN (pb.ACTUAL_BUDGET - pb.PLANNED_BUDGET) / pb.PLANNED_BUDGET 
                        ELSE 0 END) * 100 as AVG_BUDGET_OVERRUN
                FROM PROJECTS p
                LEFT JOIN PROJECT_BUDGET pb ON p.PROJECT_ID = pb.PROJECT_ID
                """
                cursor = self.conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                
                return {
                    'total_projects': result[0],
                    'on_track': result[1],
                    'at_risk': result[2],
                    'delayed': result[3],
                    'avg_budget_overrun': float(result[4])
                }
                
        except Exception as e:
            logger.error(f"Error fetching project data: {str(e)}")
            return {}

    def get_risk_assessment(self, project_id: str) -> Dict:
        """Get risk assessment for a specific project"""
        try:
            query = """
            SELECT 
                pr.RISK_TYPE,
                pr.SEVERITY,
                pr.PROBABILITY,
                pr.RISK_DESCRIPTION,
                pr.MITIGATION_PLAN
            FROM PROJECT_RISKS pr
            WHERE pr.PROJECT_ID = %s AND pr.STATUS = 'ACTIVE'
            """
            cursor = self.conn.cursor()
            cursor.execute(query, (project_id,))
            risks = cursor.fetchall()
            
            return {
                'risks': [
                    {
                        'type': risk[0],
                        'severity': risk[1],
                        'probability': risk[2],
                        'description': risk[3],
                        'mitigation': risk[4]
                    }
                    for risk in risks
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching risk assessment: {str(e)}")
            return {'risks': []}

    def process_query(self, query: str, project_id: str = None) -> str:
        """Process user query and generate response"""
        try:
            # Get relevant project data
            project_data = self.get_project_data(project_id)
            if project_id:
                risk_data = self.get_risk_assessment(project_id)
                project_data.update(risk_data)
            
            # Format project data for the prompt
            formatted_data = json.dumps(project_data, indent=2)
            
            # Generate response using LLM chain
            response = self.chain.predict(
                human_input=query,
                project_data=formatted_data
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def close(self):
        """Close Snowflake connection"""
        self.conn.close()

def main():
    chatbot = ProjectChatbot()
    try:
        print("Project Risk Assessment Chatbot")
        print("Type 'exit' to quit")
        print("\nYou can ask questions like:")
        print("- What's the status of project X?")
        print("- What are the current risks?")
        print("- Give me a summary of all projects")
        
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'exit':
                break
                
            response = chatbot.process_query(user_input)
            print(f"\nAI: {response}")
            
    finally:
        chatbot.close()

if __name__ == "__main__":
    main() 