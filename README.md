# Project: AI-powered Risk Assessment and Automation for Project Transformation

## 📊 **Overview**

In this project, I aim to develop a comprehensive **AI-powered solution** for assessing the **risk** in project transformations, especially in supply chain operations. This involves integrating **predictive analytics**, **automated status tracking**, and **intelligent decision-making** via a chatbot powered by **Large Language Models (LLM)**.

The project leverages **Snowflake** for data storage, **Power BI** for data visualization, **Machine Learning (ML)** for predictive analysis, and a custom-built **AI Chatbot** to track and predict the status of ongoing projects, while identifying potential risks.

---

## 🏆 **Importance**

In today's fast-paced business environment, managing complex projects, particularly in large organizations like L'Oréal, requires accurate **risk assessment**, timely **status tracking**, and **budget management**. This project is designed to:

- **Automate status updates** using AI, giving real-time insights into project progress and potential risks.
- Use **predictive analytics** to forecast risks such as budget overruns, delays, and vendor issues, enabling proactive decision-making.
- Help **transform operations** by integrating AI and data visualization tools, allowing seamless integration across teams and real-time tracking.
- Provide an intelligent **AI chatbot** for personalized risk updates and support.

---

## 🔑 **Key Technologies Used**

- **Snowflake**: Cloud-based data warehousing platform for storing and querying large project datasets.
- **Power BI**: Data visualization tool to create interactive reports and dashboards.
- **Machine Learning (ML)**: Scikit-learn, RandomForestClassifier to build a predictive model for risk assessment.
- **LangChain**: Used to create the AI-powered chatbot using GPT (OpenAI) for natural language processing.
- **Python**: The language used for data processing, ETL pipeline, and machine learning model development.
- **ETL**: Extract, Transform, Load pipeline for preparing data for analysis and storage in Snowflake.

---

## 🛠️ **Project Breakdown**

### 1. **Data Preparation & ETL Pipeline using Snowflake**

**What I'm doing:**

In this step, I am setting up a **Snowflake** database and creating an ETL pipeline to load and clean the project data. The dataset contains 10,000 project records, with metadata, budget usage, status, and delay reasons.

**Why it's important:**

- Ensures that the project data is properly structured and cleaned, making it ready for analysis.
- Snowflake's cloud-based architecture ensures scalability and performance.

**How I’m doing it:**

- Create a **Snowflake table** schema based on the dataset structure.
- Load data from a **CSV** file into Snowflake using **COPY INTO** commands.
- Develop an **ETL pipeline** in Python to clean the data and ensure quality.

### 2. **Power BI Dashboards**

**What I'm doing:**

I will create **Power BI dashboards** that allow real-time visualization of project data, tracking **status**, **budget usage**, and **risks**.

**Why it's important:**

- Interactive dashboards help monitor key project metrics and make informed decisions.
- Visualizing the project status in a **RAG** (Red, Amber, Green) format allows stakeholders to quickly understand risks and progress.

**How I’m doing it:**

- **Connect Snowflake** to Power BI for real-time data extraction.
- Build visualizations such as:
  - **Status Overview**: Distribution of project statuses (On Track, Delayed).
  - **Risk Overview**: Projects with high risks, predicted delays, and budget issues.
  - **Milestone Completion**: Tracking project completion vs. delays.

### 3. **Predictive Model for Risk Assessment**

**What I'm doing:**

I am using a **machine learning model** to predict the likelihood of project delays and risks, such as vendor issues or budget overruns, based on historical data.

**Why it's important:**

- Predictive models help stakeholders proactively manage risks and make informed decisions about how to address potential project delays before they become critical.
- Helps businesses to forecast issues and adjust their strategy accordingly.

**How I’m doing it:**

- I will train a **Random Forest Classifier** model using features like **milestone percentage**, **budget used**, **delay days**, and **vendor issues**.
- Use **Scikit-learn** to build, train, and evaluate the model.

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Prepare dataset and split into features and labels
X = df[['milestone_percentage', 'budget_used', 'delay_days']]  # Features
y = df['predicted_risk']  # Labels (High, Medium, Low)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train the model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluate the model
print(f'Accuracy: {accuracy_score(y_test, y_pred)}')
