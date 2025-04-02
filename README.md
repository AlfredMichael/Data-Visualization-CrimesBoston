
# Data-Visualization-CrimesBoston

## Overview
**Data-Visualization-CrimesBoston** is a Dash-based web application that provides insightful visualizations of crime data in Boston from 2020 to 2022. This project leverages utilizes  charts to analyze crime trends, geospatial distributions, and seasonal patterns, offering users an engaging platform for exploring street-level crime data.

## Features
- **Geospatial Visualization**: Interactive crime maps by district.
- **Basic Charts**: Bar, pie, and line charts for crime statistics.
- **Animated Time-Series**: Dynamic charts showing trends over time.
- **Polar Charts**: Seasonal crime analysis using circular visualizations.
- **Firebase Integration**: Secure data retrieval and storage.
- **Custom Dashboard UI**: Built with Dash and Bootstrap.

## Technologies Used
- **Python Libraries**: Dash, Plotly, Pandas, Dash-Bootstrap-Components
- **Database**: KaggleHub for dataset retrieval
- **Web Hosting**: Flask and Dash framework
- **Visualization Tools**: Plotly, Dash Components

## Dataset
Crime data sourced from [Data.Boston.Gov](https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system). Note: The data analyzed is limited to the years 2020-2022.

## Project Hsoted on PythonAnywhere
[mindhunter.pythonanywhere.com](https://mindhunter.pythonanywhere.com/)

## Installation
To run this project locally, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/YourGitHubUsername/Data-Visualization-CrimesBoston.git
   cd Data-Visualization-CrimesBoston
   ```

2. Install dependencies:
   ```bash
   pip install dash pandas dash-bootstrap-components kagglehub
   ```

3. Download the dataset:
   ```python
   import kagglehub
   path = kagglehub.dataset_download("fredthedev/updated-crimes-in-boston")
   ```

4. Start the Dash server:
   ```bash
   python app.py
   ```

5. Open the web application at `http://127.0.0.1:8050`.

## Usage
- Navigate through tabs to explore different visualizations:
  - **Geospatial Maps**: Select districts to view crime incidents.
  - **Charts**: Explore crime trends, category distributions, and seasonal insights.
  - **Time-Series**: Analyze how crime rates evolve over time.

## Contact
For questions or collaboration opportunities, please reach out to:
- Michael Alfred: success_fred@yahoo.com

---

Feel free to tweak the sections to fit your needs, especially the repository name and contact information. Let me know if you'd like help refining further!
