# Amazon Sales Data Analysis Dashboard

A comprehensive, AI-driven Streamlit application for analyzing and forecasting Amazon sales data. This dashboard provides deep insights into revenue, order volume, product performance, and future growth scenarios through an intuitive user interface.

## 🚀 Features

### 1. 📊 Sales Performance Dashboard (`eda.py`)
- **Comprehensive Overview:** View revenue, order volumes, and average ratings.
- **Dynamic Time Range:** Filter data by the last 3, 6, 12 months, or multiple years.
- **KPI Badges:** Interactive metrics displaying percentage changes over time.
- **Visualizations:** Line charts for revenue trends, and distribution plots for regions and payment methods.
- **Data Table:** Interactive grid view of recent orders using `streamlit-aggrid`.

### 2. 🧙‍♂️ Forecast Session (`forecast.py`)
- **AI-driven Predictions:** Utilizes the `prophet` library to generate revenue forecasts for upcoming quarters.
- **Scenario Planning:** Test out various growth scenarios (e.g., Moderate +5%, Aggressive +10%, Conservative +2%).
- **Confidence Intervals:** Visualize the projected bounds comparing historical performance versus forecasted growth.
- **Category Growth Potential:** Bar charts estimating category growth and AI-recommended inventory alerts.

### 3. 🤖 Data Analysis Agent (`ai_agent.py`)
- **Natural Language Querying:** Ask questions about your dataset in plain English using OpenAI's models (GPT-4o, GPT-4o-mini).
- **Code & Chart Generation:** The agent automatically writes valid Python code, executes it securely, and returns the result along with `matplotlib`/`seaborn` charts if applicable.
- **Schema Awareness:** Fully understands your dataset's schema mapping dates, numbers, and strings.
- *(Requires an OpenAI API Key inserted via the sidebar)*.

## 📁 Project Structure

```
Amazon Analysis/
├── assets/
│   └── styles.css              # Custom styling for the dashboard
├── components/
│   └── comp.py                 # Custom UI components like KPI badges
├── data/
│   └── amazon_sales_dataset.csv# Source dataset
├── pages/
│   ├── ai_agent.py             # Data Analysis Agent page
│   ├── eda.py                  # Exploratory Data Analysis page
│   └── forecast.py             # Forecasting page
├── services/
│   └── prophet_service.py      # Time series forecasting logic
├── utils/
│   ├── aggrid_build.py         # AG Grid implementation
│   ├── data.py                 # Data loading and metric calculators
│   └── plots.py                # Plotly chart generators
├── main.py                     # Entry point for the Streamlit app
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation & Setup

1. **Clone the repository / Navigate to the directory:**
   ```bash
   cd "Amazon Analysis"
   ```

2. **(Optional) Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   Ensure you have all the required libraries installed via `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   *Key dependencies: `streamlit`, `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `prophet`, `openai`, `st-styled`, `streamlit-aggrid`.*

4. **Run the Application:**
   ```bash
   streamlit run main.py
   ```

## 💡 Usage

- Upon running the app, use the sidebar navigation to switch between the **Dashboard**, **Forecast**, and **AI Agent** pages.
- For the **AI Agent**, provide your OpenAI API Key securely in the settings side panel before querying your data. You can choose to analyze the sample dataset or upload your own CSV.

## 📄 License
© 2026 DatabuildAI. Developed by [DataBuildAI](https://databuildai.com).
