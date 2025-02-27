#!/usr/bin/env python
# coding: utf-8

# Install neccessary libraries for data manipulation and visualization

# In[3]:


get_ipython().system('pip install dash')
get_ipython().system('pip install pandas')
get_ipython().system('pip install dash-bootstrap-components')
get_ipython().system('pip install kagglehub')


# Load up and clean dataset

# In[9]:

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import calendar
import random
import pandas as pd
import kagglehub

# crime_file = "dataset/crime.csv"
# Download the latest version of the dataset
path = kagglehub.dataset_download("fredthedev/updated-crimes-in-boston")

print("Path to dataset files:", path)

# Load the dataset from the downloaded path
crime_file = f"{path}/NewCombinedCrimeBoston.csv"

'''
latin1 can handle more characters than the default
UTF-8 fails
'''
df = pd.read_csv(crime_file, encoding='latin1')

# The SHOOTING column is empty so remove it from the dataframe
df = df.drop(columns=['SHOOTING'])

# Fill empty cells in REPORTING_AREA with 0
df['REPORTING_AREA'] = df['REPORTING_AREA'].fillna('0')

# Fill empty cells in specific columns with appropriate values
df['DISTRICT'] = df['DISTRICT'].fillna('Other')
df['UCR_PART'] = df['UCR_PART'].fillna('Other')
df['STREET'] = df['STREET'].fillna('Other')
df['Lat'] = df['Lat'].fillna(0.0)
df['Long'] = df['Long'].fillna(0.0)

# Replace OFFENSE_CODE_GROUP values with OFFENSE_DESCRIPTION values as 2019 -2025 all have offense description instead
df['OFFENSE_CODE_GROUP'] = df['OFFENSE_DESCRIPTION']

# Drop rows where Lat and Long are both 0.0
df = df[(df['Lat'] != 0.0) & (df['Long'] != 0.0)]



# In[11]:




# Remove the timezone information and convert the date column into a datetime object
df['OCCURRED_ON_DATE'] = df['OCCURRED_ON_DATE'].str.split('+', n=1).str[0]

# Convert the date column into a datetime object with the specified format
df['OCCURRED_ON_DATE'] = pd.to_datetime(df['OCCURRED_ON_DATE'], format='%Y-%m-%d %H:%M:%S')

# Extract day and month for our slider and map
df['day'] = df['OCCURRED_ON_DATE'].dt.day
df['month'] = df['OCCURRED_ON_DATE'].dt.strftime('%B')

# Extract year for our map
df['YEAR'] = df['OCCURRED_ON_DATE'].dt.year



# Get the list of unique districts
districts = sorted(df['DISTRICT'].unique().tolist())
districts.insert(0, "All Districts")

# Get the list of unique parts
parts = sorted(df['UCR_PART'].unique().tolist())
parts.insert(0, "All Parts")

# Get a sorted list of unique years
years = sorted(df['YEAR'].unique().tolist())
years.insert(0, "All Years")

# Get a sorted list of unique months
months = sorted(df['month'].unique().tolist(), key=lambda x: pd.to_datetime(x, format='%B').month)
months.insert(0, "All Months")

# Get the list of unique streets
streets = sorted(df['STREET'].unique().tolist())
streets.insert(0, "All Streets")




# Group by DISTRICT, STREET, and OFFENSE_CODE_GROUP to count the number of offenses
crime_by_street = df.groupby(['DISTRICT', 'STREET', 'OFFENSE_CODE_GROUP']).size().reset_index(name='OFFENSE_COUNT')

# Merge the count data back with the original DataFrame to include Lat and Long
df = df.merge(crime_by_street, on=['DISTRICT', 'STREET', 'OFFENSE_CODE_GROUP'], suffixes=('', '_y'))

# Select a random latitude and longitude from the dataset
random_index = random.randint(0, len(df) - 1)
random_lat = df.iloc[random_index]['Lat']
random_lon = df.iloc[random_index]['Long']


# In[13]:





# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Set the favicon
app._favicon = "images/bostonicon.png"

# Define the layout
app.layout = html.Div(
    children=[
        dbc.Navbar(
            dbc.Container(
                [
                    # Left icon
                    dbc.NavbarBrand(
                        html.Img(src="/assets/images/bostonicon.png", height="70px"),
                        className="me-auto",
                    ),
                    # Center text
                    dbc.NavbarBrand(
                        html.B("Street-Level Crime Analysis in Boston"),
                        className="mx-auto"
                    ),
                    # Right icon
                    dbc.NavbarBrand(
                        html.Img(src="/assets/images/tus.png", height="30px"),
                        className="ms-auto",
                    ),
                ]
            ),
            color="light",
            className="navbar-light navbar-shadow",
        ),
        dcc.Tabs(id="web-tabs", value='tab-1', children=[
            dcc.Tab(label='Geospatial Visualization', value='tab-1'),
            dcc.Tab(label='Basic Charts', value='tab-2'),
            dcc.Tab(label='Animated Time-Series Charts', value='tab-3'),
            dcc.Tab(label='Polar Charts (Seasons)', value='tab-4'),
        ]),

        html.Div(id='tabs-content')

    ]
)
#==================================================================UI CALLBACKS===============================================================================

@app.callback(
    dash.dependencies.Output('tabs-content', 'children'),
    [dash.dependencies.Input('web-tabs', 'value')]
)
def render_content(tab):
    # container for district dropdown
    if tab == 'tab-1':
      return dbc.Container(
            [
                html.P(
                    "Data Source: https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system, please note data is limited from 2020 to 2022..",
                    style={'textAlign': 'center'}
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id='district-dropdown',
                                options=[{'label': district, 'value': district} for district in districts],
                                value=districts[0],
                                placeholder="Select a district"
                            ),
                            width=3
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='street-dropdown',
                                options=[{'label': street, 'value': street} for street in streets],
                                value=streets[0],
                                placeholder="Select a street"
                            ),
                            width=7
                        ),

                        dbc.Col(
                            dcc.Dropdown(
                                id='ucr-part-dropdown',
                                options=[{'label': part, 'value': part} for part in parts],
                                value=parts[0],
                                placeholder="Select a UCR part"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='year-dropdown',
                                options=[{'label': year, 'value': year} for year in years if year != "All Years"],
                                value=years[1] if len(years) > 1 and years[0] == "All Years" else years[0],
                                placeholder="Select a year"
                            ),
                            width=2
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id='month-dropdown',
                                options=[{'label': month, 'value': month} for month in months],
                                value=months[0],
                                placeholder="Select a month"
                            ),
                            width=2
                        )
                    ],
                    justify="center"
                ),
                html.Br(),
                dbc.Row(
                    [
                        dcc.RangeSlider(
                            id='date-slider',
                            min=1,
                            max=31,  # Maximum number of days in a month
                            value=[1, 31],
                            marks={i: str(i) for i in range(1, 32)},
                            step=1
                        )
                    ]
                ),
                html.Br(),

                html.Br(),
                dcc.Graph(
                    id="mapbox-plot",
                    config={"displayModeBar": True}  # shows a toolbar for additional interactivity
                ),
                html.Br(),
                html.P(
                    "This map visualizes street-level crime data in Boston. data can be filtered based on various parameters such as district, street, UCR part, year, month, and day range. The map displays the lat and long of crimes, with markers sized according to the number of offenses at each location. The markers are colored based on the type of offense, allowing users to quickly identify areas with high crime rates and the nature of crimes committed.",
                    style={'textAlign': 'center'}
                ),
                html.Div(id='offense-summary')


            ],
            className="mt-4"
        )
    elif tab == 'tab-2':
      return dbc.Container(
            [
                html.P(
                    "Data Source: https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system, please note data is limited from 2020 to 2022..",
                    style={'textAlign': 'center'}
                ),
                html.Br(),

                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id='basic-charts-month-dropdown',
                                options=[{'label': month, 'value': month} for month in months],
                                value=months[0],
                                placeholder="Select a month"
                            ),
                            width=2
                        ),

                        dbc.Col(
                            dcc.Dropdown(
                                id='basic-charts-year-dropdown',
                                options=[{'label': year, 'value': year} for year in years],
                                value=years[0],
                                placeholder="Select a year"
                            ),
                            width=2
                        ),
                       ],
                    justify="center"
                ),

                html.Br(),
                dcc.Graph(
                    id="bar-chart",
                    config={"displayModeBar": True}
                ),
                html.Br(),
                html.P(
                    "This bar chart visualizes the distribution of crime incidents across different hours of the day. The data can be filtered based on a selected month or and year to provide specific insights into crime patterns. The chart helps identify peak crime hours, aiding in law enforcement planning and public safety awareness.",
                    style={'textAlign': 'center'}
                ),

                html.Br(),
                dcc.Graph(
                    id="line-chart",
                    config={"displayModeBar": True}
                ),
                html.Br(),
                html.P(
                    "This line chart visualizes the distribution of crime incidents across different days of the week and offense code groups. The data can be filtered based on a selected year and month to provide specific insights into crime patterns. The chart helps identify which days of the week are more prone to specific types of crimes, aiding in law enforcement resource allocation and public safety awareness.",
                    style={'textAlign': 'center'}
                ),


                html.Br(),
                dcc.Graph(
                    id="district-bar-chart",
                    config={"displayModeBar": True}
                ),
                html.Br(),
                html.P(
                    "This stacked bar chart visualizes the distribution of crime incidents across different districts and offense code groups. The data can be filtered based on a selected month or and year to provide specific insights into crime patterns. The chart helps identify which districts are more prone to specific types of crimes, aiding in law enforcement resource allocation and public safety awareness.",
                    style={'textAlign': 'center'}
                ),

            ],
            className="mt-4"
        )
    elif tab == 'tab-3':
      return dbc.Container(
            [
                html.P(
                    "Data Source: https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system, please note data is limited from 2020 to 2022..",
                    style={'textAlign': 'center'}
                ),
                html.Br(),

                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Dropdown(
                                id='time-district-dropdown',
                                options=[{'label': district, 'value': district} for district in districts],
                                value=districts[0],
                                placeholder="Select a district"
                            ),
                            width=2
                        ),

                        dbc.Col(
                            dcc.Dropdown(
                                id='time-ucr-part-dropdown',
                                options=[{'label': part, 'value': part} for part in parts],
                                value=parts[0],
                                placeholder="Select a UCR part"
                            ),
                            width=2
                        ),

                        dbc.Col(
                            dcc.Dropdown(
                                id='time-offense-group-dropdown',
                                placeholder="Select an offense code group"
                            ),
                            width=7
                        ),

                        dbc.Col(
                           dcc.Dropdown(
                                id='time-year-dropdown',
                                options=[{'label': year, 'value': year} for year in years if year != "All Years"],
                                value=years[1],  # Set the default to an actual year (e.g., the first year)
                                placeholder="Select a year"
                            ),
                            width=2
                        ),
                       ],
                    justify="center"
                ),
                html.Br(),

                dcc.Graph(
                    id="animated-mapbox-plot",
                    config={"displayModeBar": True}  # shows a toolbar for additional interactivity
                ),
                html.P(
                    "This animated time series chart visualizes the evolution of specific crimes in various districts and cities over the years, offering a clear view of trends and patterns in crime rates.",
                    style={'textAlign': 'center'}
                ),


            ],
            className="mt-4"
        )
    elif tab == 'tab-4':
      return dbc.Container(
          [
              html.P(
                    "Data Source: https://data.boston.gov/dataset/crime-incident-reports-august-2015-to-date-source-new-system, please note data is limited from 2020 to 2022..",
                    style={'textAlign': 'center'}
                ),
              dbc.Row(html.Div(), style={'margin-top': '35px'}),
              dbc.Row(
                  [
                      html.Br(),
                      dbc.Col(
                          dcc.Dropdown(
                              id = 'polar-unique-districts',
                              options=[{'label': district, 'value': district} for district in districts],
                              value=districts[0],
                              placeholder="Select a district"
                            ),
                            width=2
                      ),
                      dbc.Col(
                          dcc.Dropdown(
                              id = 'polar-unique-streets',
                              placeholder="Select a street"
                            ),
                            width=7
                      ),
                      dbc.Col(
                          dcc.Dropdown(
                              id = 'polar-unique-ucrparts',
                              options=[{'label': part, 'value': part} for part in parts],
                              value=parts[0],
                              placeholder="Select a UCR part"
                            ),
                            width=2
                      ),
                      dbc.Col(
                          dcc.Dropdown(
                              id = 'polar-unique-offensecodegrp',
                              placeholder="Select an offence code group"
                            ),
                            width=7
                      ),
                      dbc.Col(
                          dcc.Dropdown(
                              id = 'polar-unique-years',
                              options=[{'label': year, 'value': year} for year in years if year != "All Years"],
                              value=years[1],  # Set the default to the first year
                              placeholder="Select a year"
                            ),
                            width=2
                      ),

                  ],
                justify="center"
              ),
              html.Br(),
              dcc.Graph(id='polar-chart'),
              html.Div([
                html.Button('Back', id='back-button', className='button'),
                html.Button('Drill Down', id='drilldown-button', className='button')
            ], style={'display': 'flex', 'justify-content': 'center', 'gap': '18px'}),

              html.Div(id='summary-text', style={'textAlign': 'center', 'marginTop': '20px'})
          ]

      )

#==================================================================END UI CALLBACKS===============================================================================


#==================================================================FUNCTIONALITY CALLBACKS===============================================================================
# Callback to update the date slider based on the selected year and month
@app.callback(
    Output('date-slider', 'max'),
    Output('date-slider', 'value'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value')
)
def update_date_slider(selected_year, selected_month):
    # Check if "All Years" or "All Months" is selected
    if selected_year == "All Years" or selected_month == "All Months":
        max_value = 31  # Default maximum days in a month
        value = [1, 31]  # Default range
    else:
        # Get the number of days in the selected month and year
        num_days = pd.to_datetime(f'{selected_year}-{selected_month}-01').days_in_month
        max_value = num_days
        value = [1, num_days]  # Initial range

    return max_value, value


# Callback to update the street dropdown based on the selected district
@app.callback(
    Output('street-dropdown', 'options'),
    Input('district-dropdown', 'value')
)
def update_street_dropdown(selected_district):
    if selected_district == "All Districts":
        # If "All Districts" is selected, show all streets
        streets = sorted(df['STREET'].unique().tolist())
    else:
        # Filter the dataframe for the selected district
        filtered_df = df[df['DISTRICT'] == selected_district]
        # Get unique streets for the selected district
        streets = sorted(filtered_df['STREET'].unique().tolist())
    # Add "All Streets" to the list of streets
    streets.insert(0, "All Streets")
    # Return options for the street dropdown
    return [{'label': street, 'value': street} for street in streets]


# Callback to update the map based on the selected district, street, UCR part, year, and month
@app.callback(
    Output('mapbox-plot', 'figure'),
    Input('district-dropdown', 'value'),
    Input('street-dropdown', 'value'),
    Input('ucr-part-dropdown', 'value'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('date-slider', 'value')
)
def update_map(selected_district, selected_street, selected_ucr_part, selected_year, selected_month, selected_days):
    # Filter the dataframe based on the selected district, street, UCR part, year, and month
    filtered_df = df.copy()
    if selected_district != "All Districts":
        filtered_df = filtered_df[filtered_df['DISTRICT'] == selected_district]
    if selected_street != "All Streets":
        filtered_df = filtered_df[filtered_df['STREET'] == selected_street]
    if selected_ucr_part != "All Parts":
        filtered_df = filtered_df[filtered_df['UCR_PART'] == selected_ucr_part]
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['YEAR'] == int(selected_year)]
    if selected_month != "All Months":
        filtered_df = filtered_df[filtered_df['month'] == selected_month]
    if selected_days:
        filtered_df = filtered_df[(filtered_df['day'] >= selected_days[0]) & (filtered_df['day'] <= selected_days[1])]


    # Select a random latitude and longitude from the filtered dataset for centering the map
    if len(filtered_df) > 0:
        random_index = random.randint(0, len(filtered_df) - 1)
        random_lat = filtered_df.iloc[random_index]['Lat']
        random_lon = filtered_df.iloc[random_index]['Long']
    else:
        random_lat = df.iloc[0]['Lat']
        random_lon = df.iloc[0]['Long']

    # Create a scatter mapbox plot
    fig_mapbox = px.scatter_mapbox(
        filtered_df,
        lat="Lat",
        lon="Long",
        size="OFFENSE_COUNT",
        color="OFFENSE_CODE_GROUP",
        hover_name="STREET",
        hover_data={
            "OFFENSE_COUNT": True,
            "DISTRICT": True,
            "day": True,
            "month": True,
            "YEAR": True,
            "UCR_PART": True,
            "OFFENSE_CODE_GROUP": True
        },
        width=1650,
        zoom=10,  # Adjust the zoom level as needed
        center={"lat": random_lat, "lon": random_lon},  # Center the map around the data
        mapbox_style="open-street-map",
        title="Crime Share by Street and Offense Type"
    )

    fig_mapbox.update_layout(
        mapbox=dict(
            style="open-street-map",
            pitch=45,  # 3D-like perspective (0 to 60 is nice)
            bearing=20  # Change  camera angle horizontally, max 360
        ),
        height=950
    )

    return fig_mapbox


# Callback to update the offense summary based on the selected filters
@app.callback(
    Output('offense-summary', 'children'),
    Input('district-dropdown', 'value'),
    Input('street-dropdown', 'value'),
    Input('ucr-part-dropdown', 'value'),
    Input('year-dropdown', 'value'),
    Input('month-dropdown', 'value'),
    Input('date-slider', 'value')
)
def update_offense_summary(selected_district, selected_street, selected_ucr_part, selected_year, selected_month, selected_days):
    # Filter the dataframe based on the selected district, street, UCR part, year, month, and day range
    filtered_df = df.copy()
    if selected_district != "All Districts":
        filtered_df = filtered_df[filtered_df['DISTRICT'] == selected_district]
    if selected_street != "All Streets":
        filtered_df = filtered_df[filtered_df['STREET'] == selected_street]
    if selected_ucr_part != "All Parts":
        filtered_df = filtered_df[filtered_df['UCR_PART'] == selected_ucr_part]
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['YEAR'] == int(selected_year)]
    if selected_month != "All Months":
        filtered_df = filtered_df[filtered_df['month'] == selected_month]
    if selected_days:
        filtered_df = filtered_df[(filtered_df['day'] >= selected_days[0]) & (filtered_df['day'] <= selected_days[1])]

    # Check if the filtered dataframe is empty
    if filtered_df.empty:
        return "No data available for the selected filters. Please try modifying the filters."

    # Calculate the count of cases for each offense code group
    offense_counts = filtered_df.groupby('OFFENSE_CODE_GROUP')['INCIDENT_NUMBER'].count().reset_index(name='COUNT')
    offense_counts = offense_counts.sort_values(by='COUNT', ascending=False)

    # Find the most common crime
    most_common_crime = offense_counts.iloc[0]['OFFENSE_CODE_GROUP'] if not offense_counts.empty else 'N/A'

    # Create the summary text
    offense_summary = [
        html.P(f"Most common offence: {most_common_crime}"),
        html.P(f"Total number of cases: {len(filtered_df)}"),
        html.P("Count of cases for each offense code group:"),
        html.Ul([html.Li(f"{row['OFFENSE_CODE_GROUP']}: {row['COUNT']} cases") for index, row in offense_counts.iterrows()])

    ]

    return offense_summary

#------------------------------------------------------------- Tab 2 --------------------------------------------------------------------------------
# Callback to generate the bar chart
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('basic-charts-month-dropdown', 'value'),
     Input('basic-charts-year-dropdown', 'value')]
)
def update_bar_chart(selected_month, selected_year):
    # Filter data based on the selected month and year
    if selected_month != "All Months":
        df_filtered = df[df['month'] == selected_month]
    else:
        df_filtered = df.copy()

    if selected_year != "All Years":
        df_filtered = df_filtered[df_filtered['YEAR'] == selected_year]
    else:
        df_filtered = df_filtered

    # Group data by hour and count incidents
    hourly_counts = df_filtered['HOUR'].value_counts().reset_index()
    hourly_counts.columns = ['Hour', 'Incident Count']
    hourly_counts = hourly_counts.sort_values(by='Hour')

    # Create a bar chart
    fig = px.bar(hourly_counts, x='Hour', y='Incident Count',
                 title='Crime Clock - 24-hour Distribution',
                 labels={'Hour': 'Hour of the Day', 'Incident Count': 'Number of Incidents'})

    # Customize the layout for better visualization
    fig.update_layout(
        xaxis=dict(
            dtick=1,  # Ensure all hours are shown
            tickmode='linear'
        ),
        yaxis=dict(
            title='Number of Incidents'
        ),
        title={
            'text': "Crime O'Clock - 24-hour Distribution",
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    return fig


# Callback to generate the stacked bar chart for District Crime Profile
@app.callback(
    Output('district-bar-chart', 'figure'),
    [Input('basic-charts-month-dropdown', 'value'),
     Input('basic-charts-year-dropdown', 'value')]
)
def update_district_bar_chart(selected_month, selected_year):
    # Filter data based on the selected month and year
    if selected_month != "All Months":
        df_filtered = df[df['month'] == selected_month]
    else:
        df_filtered = df.copy()

    if selected_year != "All Years":
        df_filtered = df_filtered[df_filtered['YEAR'] == selected_year]
    else:
        df_filtered = df_filtered

    # Group data by district and offense code group, count incidents
    district_offense_counts = df_filtered.groupby(['DISTRICT', 'OFFENSE_CODE_GROUP']).size().reset_index(name='Incident Count')

    # Create a bar chart
    fig = px.bar(district_offense_counts, x='DISTRICT', y='Incident Count', color='OFFENSE_CODE_GROUP',
                 title='District Crime Profile - Incident Count by District and Offense Code Group',
                 labels={'DISTRICT': 'District', 'Incident Count': 'Number of Incidents', 'OFFENSE_CODE_GROUP': 'Offense Code Group'})


    fig.update_layout(
        xaxis=dict(title='District'),
        yaxis=dict(title='Number of Incidents'),
        title={
            'text': 'District Crime Profile - Incident Count by District and Offense Code Group',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1700,
        margin=dict(r=200),
    )
    return fig


# Callback to generate line chart that showcases weekly crime patterns
@app.callback(
    Output('line-chart', 'figure'),
    [Input('basic-charts-year-dropdown', 'value'),
     Input('basic-charts-month-dropdown', 'value')]
)
def update_line_chart(selected_year, selected_month):
    # Filter data based on the selected year and month
    df_filtered = df.copy()

    if selected_year != "All Years":
        df_filtered = df_filtered[df_filtered['YEAR'] == selected_year]

    if selected_month != "All Months":
        df_filtered = df_filtered[df_filtered['month'] == selected_month]

    # Group data by day of the week and offense code group, count incidents
    weekly_offense_counts = df_filtered.groupby(['DAY_OF_WEEK', 'OFFENSE_CODE_GROUP']).size().reset_index(name='Incident Count')

    # Sort the days of the week for proper representation
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_offense_counts['DAY_OF_WEEK'] = pd.Categorical(weekly_offense_counts['DAY_OF_WEEK'], categories=day_order, ordered=True)
    weekly_offense_counts = weekly_offense_counts.sort_values('DAY_OF_WEEK')

    # Create a line chart
    fig = px.line(weekly_offense_counts, x='DAY_OF_WEEK', y='Incident Count', color='OFFENSE_CODE_GROUP',
                  title='Weekly Crime Pattern - Incident Count by Day of the Week and Offense Code Group',
                  labels={'DAY_OF_WEEK': 'Day of the Week', 'Incident Count': 'Number of Incidents', 'OFFENSE_CODE_GROUP': 'Offense Code Group'})

    # Customize the layout for better visualization
    fig.update_layout(
        xaxis=dict(title='Day of the Week'),
        yaxis=dict(title='Number of Incidents'),
        title={
            'text': 'Weekly Crime Pattern - Incident Count by Day of the Week and Offense Code Group',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1700,
        margin=dict(r=200),
    )

    return fig


#-------------------------------------------------------------------------Tab 3-------------------------------------------------------------------------
@app.callback(
    Output('time-offense-group-dropdown', 'options'),
    [Input('time-ucr-part-dropdown', 'value')]
)
def update_offense_group_dropdown(selected_part):
    if selected_part != "All Parts":
        filtered_df = df[df['UCR_PART'] == selected_part]
    else:
        filtered_df = df.copy()

    offense_groups = filtered_df['OFFENSE_CODE_GROUP'].unique().tolist()
    offense_groups.sort()
    options = [{'label': offense, 'value': offense} for offense in offense_groups]

    return options




@app.callback(
    Output('animated-mapbox-plot', 'figure'),
    [Input('time-district-dropdown', 'value'),
     Input('time-ucr-part-dropdown', 'value'),
     Input('time-year-dropdown', 'value'),
     Input('time-offense-group-dropdown', 'value')]
)
def update_animated_mapbox(selected_district, selected_part, selected_year, selected_offense_group):
    # Filter data based on the selected year
    df_filtered = df[df['YEAR'] == selected_year]

    # Filter data based on the selected district
    if selected_district != "All Districts":
        df_filtered = df_filtered[df_filtered['DISTRICT'] == selected_district]

    # Filter data based on the selected UCR part
    if selected_part != "All Parts":
        df_filtered = df_filtered[df_filtered['UCR_PART'] == selected_part]

    # Filter data based on the selected offense code group
    if selected_offense_group:
        df_filtered = df_filtered[df_filtered['OFFENSE_CODE_GROUP'] == selected_offense_group]

    # Extract month and day for animation
    df_filtered['Month'] = df_filtered['OCCURRED_ON_DATE'].dt.month_name()
    df_filtered['Month_num'] = df_filtered['OCCURRED_ON_DATE'].dt.month
    df_filtered['Day'] = df_filtered['OCCURRED_ON_DATE'].dt.day

    # Sort the data by month and remove months without data
    df_filtered = df_filtered.sort_values('Month_num')
    df_filtered = df_filtered[df_filtered.groupby('Month')['Month'].transform('count') > 0]

    # Create an animated Mapbox plot
    fig = px.scatter_mapbox(
        df_filtered,
        lat='Lat',
        lon='Long',
        animation_frame='Month',
        color='OFFENSE_CODE_GROUP',
        hover_name='OFFENSE_DESCRIPTION',
        hover_data={'DISTRICT': True, 'STREET': True},
        title='Crime Migration Over Time',
        labels={'Lat': 'Latitude', 'Long': 'Longitude', 'OFFENSE_CODE_GROUP': 'Crime Type'},
        size='OFFENSE_COUNT',
        mapbox_style="open-street-map",
        zoom=10
    )

    fig.update_layout(
        title={
            'text': 'Crime Migration Over Time',
            'x': 0.5,
            'xanchor': 'center'
        },
        width=1700,
        mapbox=dict(center=dict(lat=random_lat, lon=random_lon), zoom=10),
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return fig

#-------------------------------------------------------------------------Tab 4-------------------------------------------------------------------------

# Callback to update the streets dropdown in Tab 4 based on the selected district
@app.callback(
    Output('polar-unique-streets', 'options'),
    Output('polar-unique-streets', 'value'),
    Input('polar-unique-districts', 'value')
)
def update_polar_streets_dropdown(selected_district):
    if selected_district == "All Districts":
        streets = sorted(df['STREET'].unique().tolist())
    else:
        filtered_df = df[df['DISTRICT'] == selected_district]
        streets = sorted(filtered_df['STREET'].unique().tolist())
    streets.insert(0, "All Streets")
    default_street = streets[0] if streets else None
    return [{'label': street, 'value': street} for street in streets], default_street

# Callback to update the offense code group dropdown in Tab 4 based on the selected UCR part
@app.callback(
    Output('polar-unique-offensecodegrp', 'options'),
    Output('polar-unique-offensecodegrp', 'value'),
    Input('polar-unique-ucrparts', 'value')
)
def update_polar_offensecodegrp_dropdown(selected_ucr_part):
    if selected_ucr_part == "All Parts":
        offense_code_groups = sorted(df['OFFENSE_CODE_GROUP'].unique().tolist())
    else:
        filtered_df = df[df['UCR_PART'] == selected_ucr_part]
        offense_code_groups = sorted(filtered_df['OFFENSE_CODE_GROUP'].unique().tolist())
    offense_code_groups.insert(0, "All Offense Code Groups")
    default_offense = offense_code_groups[0] if offense_code_groups else None
    return [{'label': group, 'value': group} for group in offense_code_groups], default_offense

# Callback to update the polar chart and summary text based on selected parameters and buttons
@app.callback(
    [Output('polar-chart', 'figure'),
     Output('summary-text', 'children')],
    [Input('polar-unique-districts', 'value'),
     Input('polar-unique-streets', 'value'),
     Input('polar-unique-ucrparts', 'value'),
     Input('polar-unique-offensecodegrp', 'value'),
     Input('polar-unique-years', 'value'),
     Input('back-button', 'n_clicks'),
     Input('drilldown-button', 'n_clicks')]
)
def update_polar_chart(selected_district, selected_street, selected_ucr_part, selected_offense_code_group, selected_year, back_clicks, drilldown_clicks):
    # Determine the chart state based on button clicks
    chart_state = 'season'
    if drilldown_clicks and (drilldown_clicks > (back_clicks or 0)):
        chart_state = 'month'

    # Filter the DataFrame
    filtered_df = df.copy()
    if selected_year != "All Years":
        filtered_df = filtered_df[filtered_df['YEAR'] == selected_year]
    if selected_street != "All Streets":
        filtered_df = filtered_df[filtered_df['STREET'] == selected_street]
    if selected_ucr_part != "All Parts":
        filtered_df = filtered_df[filtered_df['UCR_PART'] == selected_ucr_part]
    if selected_offense_code_group != "All Offense Code Groups":
        filtered_df = filtered_df[filtered_df['OFFENSE_CODE_GROUP'] == selected_offense_code_group]

    if chart_state == 'month':
        monthly_counts = filtered_df.groupby("month").size().reset_index(name="count")
        monthly_counts['month_order'] = monthly_counts['month'].apply(lambda x: list(calendar.month_name).index(x))
        monthly_counts = monthly_counts.sort_values("month_order")
        data = go.Scatterpolar(
            r = monthly_counts["count"],
            theta = monthly_counts["month"],
            mode = 'lines+markers',
            line = dict(shape='spline'),
            text = [f"Crime Count: {count}<br>Month: {month}" for count, month in zip(monthly_counts["count"], monthly_counts["month"])],
            hoverinfo = 'text'
        )
        title_text = f"Crime Offense Counts by Month"

        # Find the month with the highest crime count
        if not monthly_counts.empty:
            most_common_month = monthly_counts.loc[monthly_counts['count'].idxmax()]['month']
            summary_text = f"The selected crime occurs mostly in {most_common_month}."
        else:
            most_common_month = "N/A"
            summary_text = "No data available for the selected filters."

    else:
        def get_season(month):
            if month in ['December', 'January', 'February']:
                return 'Winter'
            elif month in ['March', 'April', 'May']:
                return 'Spring'
            elif month in ['June', 'July', 'August']:
                return 'Summer'
            else:
                return 'Autumn'

        filtered_df['season'] = filtered_df['month'].apply(get_season)
        seasonal_counts = filtered_df.groupby("season").size().reset_index(name="count")
        season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
        seasonal_counts['season'] = pd.Categorical(seasonal_counts['season'], categories=season_order, ordered=True)
        seasonal_counts = seasonal_counts.sort_values("season")
        data = go.Scatterpolar(
            r = seasonal_counts["count"],
            theta = seasonal_counts["season"],
            mode = 'lines+markers',
            line = dict(shape='spline'),
            text = [f"Crime Count: {count}<br>Season: {season}" for count, season in zip(seasonal_counts["count"], seasonal_counts["season"])],
            hoverinfo = 'text'
        )
        title_text = f"Crime Offense Counts by Season"

        # Find the season with the highest crime count
        if not seasonal_counts.empty:
            most_common_season = seasonal_counts.loc[seasonal_counts['count'].idxmax()]['season']
            summary_text = f"The selected crime occurs mostly in {most_common_season}."
        else:
            most_common_season = "N/A"
            summary_text = "No data available for the selected filters."


    if selected_year != "All Years":
        title_text += f" for {selected_year}"
    if selected_street != "All Streets":
        title_text += f" on {selected_street}"
    if selected_ucr_part != "All Parts":
        title_text += f" for {selected_ucr_part}"
    if selected_offense_code_group != "All Offense Code Groups":
        title_text += f" ({selected_offense_code_group})"

    fig = go.Figure(data=data)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, title="Offense Count")
        ),
        title=title_text
    )

    return fig, summary_text

#==================================================================END FUNCTIONALITY CALLBACKS===============================================================================

# Run the app

# Expose the server variable for WSGI to use
server = app.server

# Run the app
#if __name__ == "__main__":
    #app.run_server(debug=True)


# In[ ]:




