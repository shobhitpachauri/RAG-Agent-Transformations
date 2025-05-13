# AI-powered Risk Assessment and Automation for Project Transformation

This project implements an end-to-end system for assessing project transformation risks in supply chain operations using AI and data analytics.

## Project Components

1. **Data Pipeline**
   - Snowflake ETL pipeline for data ingestion and processing
   - Data cleaning and transformation scripts

2. **Analytics & Visualization**
   - Power BI dashboards for project monitoring
   - SQL queries for data extraction

3. **Machine Learning**
   - Random Forest classifier for risk prediction
   - Feature engineering and model evaluation

4. **AI Chatbot**
   - LangChain and OpenAI GPT integration
   - Interactive project status and risk assessment

## Setup Instructions

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   - Copy `.env.example` to `.env`
   - Update the environment variables with your credentials

3. **Database Setup**
   - Run the Snowflake schema creation script
   - Execute the ETL pipeline

## Project Structure

```
├── data/                   # Data files and datasets
├── src/                    # Source code
│   ├── etl/               # ETL pipeline scripts
│   ├── ml/                # Machine learning models
│   ├── chatbot/           # AI chatbot implementation
│   └── utils/             # Utility functions
├── sql/                   # SQL queries for Snowflake
├── notebooks/             # Jupyter notebooks for analysis
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── .env.example          # Environment variables template
```

## Dependencies

- Python 3.8+
- Snowflake
- Power BI
- OpenAI API
- LangChain

## Usage

1. Run the ETL pipeline:
   ```bash
   python src/etl/pipeline.py
   ```

2. Train the ML model:
   ```bash
   python src/ml/train_model.py
   ```

3. Start the chatbot:
   ```bash
   python src/chatbot/main.py
   ```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.