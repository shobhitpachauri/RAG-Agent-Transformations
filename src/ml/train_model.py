import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import snowflake.connector
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class RiskPredictionModel:
    def __init__(self):
        self.conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        self.model = None
        self.preprocessor = None

    def fetch_data(self):
        """Fetch data from Snowflake for model training"""
        query = """
        SELECT 
            p.PROJECT_TYPE,
            p.PRIORITY,
            DATEDIFF('day', p.START_DATE, p.PLANNED_END_DATE) as PLANNED_DURATION,
            pb.PLANNED_BUDGET,
            pb.ACTUAL_BUDGET,
            COUNT(pr.RISK_ID) as ACTIVE_RISKS,
            COUNT(pd.DELAY_ID) as TOTAL_DELAYS,
            CASE 
                WHEN COUNT(pd.DELAY_ID) > 0 OR pb.ACTUAL_BUDGET > pb.PLANNED_BUDGET THEN 1
                ELSE 0
            END as RISK_FLAG
        FROM PROJECTS p
        LEFT JOIN PROJECT_BUDGET pb ON p.PROJECT_ID = pb.PROJECT_ID
        LEFT JOIN PROJECT_RISKS pr ON p.PROJECT_ID = pr.PROJECT_ID AND pr.STATUS = 'ACTIVE'
        LEFT JOIN PROJECT_DELAYS pd ON p.PROJECT_ID = pd.PROJECT_ID
        GROUP BY 1, 2, 3, 4, 5
        """
        
        try:
            df = pd.read_sql(query, self.conn)
            logger.info(f"Fetched {len(df)} records from Snowflake")
            return df
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def prepare_features(self, df):
        """Prepare features for model training"""
        # Define categorical and numerical features
        categorical_features = ['PROJECT_TYPE', 'PRIORITY']
        numerical_features = ['PLANNED_DURATION', 'PLANNED_BUDGET', 'ACTUAL_BUDGET', 
                            'ACTIVE_RISKS', 'TOTAL_DELAYS']

        # Create preprocessing pipeline
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', StandardScaler(), numerical_features),
                ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
            ])

        # Split features and target
        X = df.drop('RISK_FLAG', axis=1)
        y = df['RISK_FLAG']

        return X, y, preprocessor

    def train_model(self, X, y, preprocessor):
        """Train the Random Forest model"""
        # Create pipeline
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(random_state=42))
        ])

        # Define parameter grid for GridSearchCV
        param_grid = {
            'classifier__n_estimators': [100, 200, 300],
            'classifier__max_depth': [10, 20, 30, None],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__min_samples_leaf': [1, 2, 4]
        }

        # Perform grid search
        grid_search = GridSearchCV(
            pipeline,
            param_grid,
            cv=5,
            scoring='f1',
            n_jobs=-1
        )

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Train model
        logger.info("Training model...")
        grid_search.fit(X_train, y_train)

        # Get best model
        self.model = grid_search.best_estimator_
        self.preprocessor = preprocessor

        # Evaluate model
        y_pred = self.model.predict(X_test)
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        logger.info("\nConfusion Matrix:")
        logger.info(confusion_matrix(y_test, y_pred))

        return self.model

    def save_model(self, model_path='models'):
        """Save the trained model and preprocessor"""
        if not os.path.exists(model_path):
            os.makedirs(model_path)

        joblib.dump(self.model, os.path.join(model_path, 'risk_prediction_model.joblib'))
        joblib.dump(self.preprocessor, os.path.join(model_path, 'preprocessor.joblib'))
        logger.info(f"Model saved to {model_path}")

    def close(self):
        """Close Snowflake connection"""
        self.conn.close()

def main():
    model_trainer = RiskPredictionModel()
    try:
        # Fetch and prepare data
        df = model_trainer.fetch_data()
        X, y, preprocessor = model_trainer.prepare_features(df)

        # Train model
        model = model_trainer.train_model(X, y, preprocessor)

        # Save model
        model_trainer.save_model()
    finally:
        model_trainer.close()

if __name__ == "__main__":
    main() 