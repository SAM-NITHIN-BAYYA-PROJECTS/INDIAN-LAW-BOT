# ⚖️ Indian Law Bot (ADK Powered)

A specialized multi-agent AI system built with the **Google Agent Development Kit (ADK)** and **Gemini 2.0 Flash Lite**. 

This bot acts as an intelligent legal intake clerk. It analyzes user queries, filters out general pleasantries, and routes complex legal issues to specific domain-expert agents trained on Indian Law (Constitution, BNS, Civil, and Traffic).

Note: This is a work in progress and is developed for a kaggle capstone project and is not to be used for any legal purposes. This can be used by common people to get a basic idea of their legal rights and obligations and lawyers to get a basic idea of their clients' legal rights and obligations and in their preparation for Bar exams.

## 🌟 Key Features

* **⚡ Optimized Orchestrator:** The Root Agent (`IndianLawBot`) now handles general greetings ("Namaste", "Hello") locally. This reduces latency and token usage by ensuring only *actual* legal queries are sent to expert sub-agents.
* **🧠 Dynamic Classification:** Uses a dedicated **Classifier Agent** that injects the user's specific text into its instructions for high-accuracy categorization.
* **🏛️ Domain-Specific Experts:**
    * **Constitution Agent:** Fundamental Rights, Citizenship, Govt Power.
    * **BNS Agent (Criminal):** Bharatiya Nyaya Sanhita sections and criminal offenses.
    * **Civil Agent:** Property disputes, contracts, family law.
    * **Traffic Agent:** Motor Vehicles Act, challans, and road safety rules.
* **🛡️ Robust Routing:** Implements regex-based validation (`re.search`) to ensure the LLM's classification matches strictly defined categories before routing.

## 🛠️ Tech Stack

* **Python 3.13**
* **Google ADK** (Agent Development Kit)
* **Google Gemini 2.0 Flash Lite** (GenAI Model)
* **Asyncio** (Asynchronous event loop)

## 📂 Project Structure

```text
Root Folder
├── law-bot
    ├── __init__.py        # Dependencies
    ├── agent.py           # Core agent logic, routing, and definitions
    ├── .env               # Environment variables
├── requirements.txt     # Project dependencies
└── README.md          # Project Documentation
```

## 📋 Prerequisites

* Python 3.13
* Google ADK
* Google Gemini 2.0 Flash Lite
* Asyncio

## How to Run

1. Clone the repository or download the zip file.
2. Extract the zip file in a directory of your choice. (Advice: Create a dedicated directory for this project.(Example: Root Folder))
3. Make sure your project directory structure is as shown in the Project Structure section.
4. Open a terminal and navigate to the directory where you extracted the zip file. (Note: Do not navigate to the law-bot directory, but the root directory of the project. (Example: Root Folder))
5. Run the following command to install the required dependencies:
```bash
pip install -r requirements.txt
```
6. Set up your Google Gemini API key in the .env file.
7. Run the following command to start the agent:
```bash
adk web
```