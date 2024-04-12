from pathlib import Path

import pandas as pd
from faicons import icon_svg
from shiny import reactive
from shiny.express import input, render, ui
from shiny.ui import output_ui
from shinywidgets import render_plotly
import plotly.express as px
from shinyswatch import theme
from shiny.express import ui

# Define the path to the Titanic dataset
titanic_path = Path(__file__).parent / "titanic_dataset.csv"

# Read the Titanic dataset into a pandas DataFrame
titanic_df = pd.read_csv(titanic_path)

# Set up the UI for the dashboard
ui.page_opts(title="Titanic Explorer", fillable=True)

with ui.sidebar():
    ui.input_select("sex", "Select Gender", choices=["male", "female"], multiple=True, selected=["male", "female"])
    ui.input_select("pclass", "Select Class", choices=["1", "2", "3"], multiple=True, selected=["1", "2", "3"])

# Define the reactive data based on the input
@reactive.calc
def filtered_data():
    selected_sexes = input.sex()  # Will be a list if multiple=True
    selected_classes = input.pclass()  # Also a list if multiple=True
    # Filter for the selected genders and classes
    filtered = titanic_df[
        titanic_df['Sex'].isin(selected_sexes) & 
        titanic_df['Pclass'].isin([int(cls) for cls in selected_classes])
    ]
    return filtered

    


# Create UI elements to display the statistics
with ui.layout_column_wrap(fill=False):
    with ui.value_box(showcase=icon_svg("users")):
        "Total Passengers"

        @render.ui
        def total_passengers():
            return str(filtered_data().shape[0])

    with ui.value_box(showcase=icon_svg("life-ring")):
        "Survivors"

        @render.ui
        def survivors():
            return str(filtered_data()[filtered_data()["Survived"] == 1].shape[0])

    with ui.value_box(showcase=icon_svg("user-slash")):
        "Non-Survivors"

        @render.ui
        def non_survivors():
            return str(filtered_data()[filtered_data()["Survived"] == 0].shape[0])

# Reactive function to generate the survival by gender chart
@reactive.calc
def survival_by_gender():
    df = filtered_data()
    return df.groupby('Sex')['Survived'].value_counts().unstack().fillna(0)

# Reactive function to generate the age distribution chart
@reactive.calc
def age_distribution():
    df = filtered_data()
    return df['Age'].dropna()  # Dropping NaN values for age


    

@render_plotly
def survival_by_gender_chart():
    df = filtered_data()
    fig = px.bar(df, 
                 x='Sex', 
                 y='Survived', 
                 color='Survived',
                 labels={'Survived': 'Survival Status', 'Sex': 'Gender'}, 
                 title="Survival Status by Gender",
                 barmode='group',
                 category_orders={"Survived": [1, 0]},  
                 color_discrete_map={0: 'tomato', 1: 'mediumseagreen'}  # Custom colors
    )

    # Improve layout aesthetics
    fig.update_layout(
        plot_bgcolor='white',  # Set the background to white for cleanliness
        paper_bgcolor='white',
        title={'text': "Survival Status by Gender", 'x': 0.5, 'xanchor': 'center'},
        margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins to fit layout
        legend_title_text='Survival Status',
        legend=dict(
            title_font_color="blue",
            y=1,  # Position the legend at the top
            x=1,
            xanchor='right',  # Anchor the legend to the right
        ),
    )

    # Customize the bar layout
    fig.update_traces(
        marker_line_color='black',
        marker_line_width=1.5,  # Adding border to bars for clear distinction
        opacity=0.9  # Making bars slightly transparent for aesthetic effect
    )
    
    # Add labels and format axes
    fig.update_xaxes(title_text='Gender', tickangle=-45)
    fig.update_yaxes(title_text='Number of Passengers', gridcolor='lightgray')  # Add gridlines for y-axis
    
    return fig

@render_plotly
def age_distribution_chart():
    df = filtered_data()
    fig = px.histogram(df, x='Age', nbins=30, title="Age Distribution",
                       color_discrete_sequence=['#3498DB'])  # Use a pleasant shade of blue

    # Improve layout aesthetics
    fig.update_layout(
        plot_bgcolor='white',  # Set the background to white for cleanliness
        paper_bgcolor='white',
        title={'text': "Age Distribution", 'x': 0.5, 'xanchor': 'center'},
        margin=dict(l=20, r=20, t=40, b=20),  # Adjust margins to fit layout
        legend_title_text='Count',
        legend=dict(
            title_font_color="blue",
            y=1,  # Position the legend at the top
            x=1,
            xanchor='right',  # Anchor the legend to the right
        ),
    )

    # Customize bar appearance
    fig.update_traces(
        marker_line_color='black',
        marker_line_width=1,  # Adding border to bars for clear distinction
        opacity=0.7  # Making bars slightly transparent for aesthetic effect
    )
    
    # Customize axes
    fig.update_xaxes(title_text='Age', tickangle=-45, showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(title_text='Count', showgrid=True, gridcolor='lightgray')

    # Optimize hover info
    fig.update_traces(hovertemplate='Age: %{x}<br>Count: %{y}')
    
    return fig
    
ui.page_opts(title="Titanic Explorer", fillable=True)
theme.darkly()
