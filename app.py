import streamlit as st
import pandas as pd
from markdown import *
import plotly.graph_objects as go
import plotly.express as px

# Set page configuration
st.set_page_config(page_title = "Family Budget App", page_icon = "💰", layout = "wide", initial_sidebar_state = "expanded",
                   menu_items = {'Get Help': 'https://www.github.com/thomazfabrin/streamlit_family_budget_app'})

# Set padding-top and padding-bottom of the main block container
st.markdown(
    """
    <style>
        .appview-container .main .block-container {{
                    padding-top: {padding_top}rem;
                    padding-bottom: {padding_bottom}rem;
                    }}

            </style>""".format(
            padding_top=1.5, padding_bottom=1, padding_left=0, padding_right=0
        ),
        unsafe_allow_html=True,
)

# Main menu
st.sidebar.title('Navigation')

# Choose a visualization
visualization = st.sidebar.radio('', ['Tutorial', 'Dashboard'])

# Tutorial page
if visualization == "Tutorial":

    st.sidebar.write('You are on the tutorial page. Follow these intructions to prepare your data \
                     and use this aplication.')

    # Load tutorial dataset
    df_tutorial = pd.read_csv('data/budget_example_dataset.csv')

    st.markdown("<h1 style='text-align: center; color: gray;'>Tutorial</h1>", unsafe_allow_html=True)
    st.write('In this tutorial, we will guide you how to prepare the dataset to use this app.')
    st.markdown("<p style='text-align: justify;'><b>Step 1:</b> Upload a CSV file containing your budget data. This dataset should contain the following columns: \
                'category', 'subcategory', 'description', 'date', 'value', and 'income'. If an item is an income, it should \
                be filled out with '1', if this is an expense, it should be '0'. You can see an example below: </p>", unsafe_allow_html=True)
    st.table(df_tutorial.head(5))
    st.markdown("<p style='text-align: justify;'><b>Step 2:</b> Once you have your dataset prepared, you can select the <b><i>Dashboard</b></i> \
                option in the Navigation menu and upload your dataset. By the way, since you keep the column names following <b>Step 1</b>, you can use your \
                categories/subcategories without any problem :) <i>HOWEVER, in order to have everything working properly, category 'Investiment' must be present.</i> \
                Also be aware that depending on your screensize you will need to close the navigation menu to see the charts properly.", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px'><i>Let's get started!</i></p>", unsafe_allow_html=True)

# Dashboard page
elif visualization == "Dashboard":

    # Upload button
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=("csv"))
        
    if uploaded_file is not None:
        st.sidebar.write('You uploaded a file!')
        df = pd.read_csv(uploaded_file) # User file
    else:
        df = pd.read_csv('data/budget_example_dataset.csv')

    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%b-%Y')
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    start_date = df['date'].min().date()
    end_date = df['date'].max().date()

    # Slider to filter dataset by date
    filter_date = st.sidebar.slider(
        "Select a date range",
        value = (start_date, end_date),
        help = 'Select a date range to filter the data',    
    )

    filter_date = pd.to_datetime(filter_date)

    df_date_filtered = df[(df['date'] >= filter_date[0]) & (df['date'] <= filter_date[1])]

    # Expenses filtered dataset by date
    df_date_filtered_expenses = df_date_filtered[df_date_filtered['income']== 0]

    # Get categories and subcategories and add multiselect widget
    categories = df_date_filtered_expenses['category'].unique()

    selected_category = st.sidebar.multiselect('Select a category', categories, 
                                               help = 'Select categories to filter the data',
                                               default = categories)
    
    df_category_filtered = df_date_filtered[df_date_filtered['category'].isin(selected_category)]

    subcategories = df_category_filtered['subcategory'].unique()

    selected_subcategory = st.sidebar.multiselect('Select a subcategory', subcategories, 
                                                  help = 'Select subcategories to filter the data',
                                                  default = subcategories)  
    
    # df_subcategory_filtered = df_category_filtered[df_category_filtered['subcategory'].isin(selected_subcategory)]

    df_complete_expenses_filtered = df_date_filtered[(df_date_filtered["category"].isin(selected_category) & df_date_filtered["subcategory"].isin(selected_subcategory))]

    col1, col2 = st.columns(2)

    # Monthly income and expenses bar chart
    with col1:

        # Create separate dataset for income and expenses
        df_income = df_date_filtered[df_date_filtered['income'] == 1]
        df_income_monthly = df_income.groupby(['month', 'year'])['value'].sum().reset_index()
        df_income_monthly['month_year'] = pd.to_datetime(df_income_monthly[['year', 'month']].assign(day=1))
        df_income_monthly = df_income_monthly.sort_values(["month", "year"])

        # df_expenses = df_complete_expenses_filtered[(df_complete_expenses_filtered['income'] == 0) & (df_complete_expenses_filtered['category'] != 'Investment')]
        df_expenses_monthly = df_complete_expenses_filtered.groupby(['month', 'year'])['value'].sum().reset_index()
        df_expenses_monthly["month_year"] = pd.to_datetime(df_expenses_monthly[['year', 'month']].assign(day=1))
        df_expenses_monthly = df_expenses_monthly.sort_values('month_year')

        # Create bar chart
        fig_monthly_bar = go.Figure()

        # Add trace for income
        fig_monthly_bar.add_trace(go.Bar(
            x = df_income_monthly['month_year'].sort_values(),
            y = df_income_monthly['value'],
            name = 'Income',
            marker_color='rgb(26, 118, 255)'
        ))

        # Add trace for expenses
        fig_monthly_bar.add_trace(go.Bar(
            x = df_expenses_monthly['month_year'].sort_values(),
            y = df_expenses_monthly['value'],
            name = 'Expenses',
            marker_color = 'rgb(55, 83, 109)'
        ))

        # Customize layout
        fig_monthly_bar.update_layout(
            title = {
                'text': 'Monthly Income and Expenses',
                'x': 0
            },
            autosize = True,
            xaxis = dict(
                tickangle = 360,
                tickfont_size = 13,
                nticks = 5
            ),
            yaxis = dict(
                title = 'Amount',
                titlefont_size = 16,
                tickfont_size = 14,
                showgrid = True
            ),
            legend = dict(
                orientation = 'h',
                x = 0.36,
                y = 1.1,
                bgcolor = 'rgba(255, 255, 255, 0)',
                bordercolor = 'rgba(255, 255, 255, 0)'
            ),
            barmode = 'group',
            bargap = 0.55,
            bargroupgap = 0.1,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        # Show plot
        st.plotly_chart(fig_monthly_bar)
    
    # Grouped expenses treemap
    with col2:

        df_expenses_category = df_complete_expenses_filtered.groupby(['category'])['value'].sum().reset_index()
        df_bills_subcategory = df_complete_expenses_filtered.groupby(['category', 'subcategory'])['value'].sum().reset_index()

        # Create labels and parents
        labels_treemap = df_expenses_category['category'].tolist() + df_bills_subcategory['subcategory'].tolist()
        parents = ['Grouped expenses'] * len(df_expenses_category['category']) + df_bills_subcategory['category'].tolist()

        # Create treemap
        fig_bills_treemap = go.Figure(go.Treemap(
            labels = labels_treemap,
            parents = parents,
            root_color = 'white',
            values = df_expenses_category['value'].tolist() + df_bills_subcategory['value'].tolist(),
            textinfo='label+value',
            textfont=dict(
                size=15,
                color='white'
            ),
            marker=dict(
                line=dict(
                    width=2
                )
            )
        ))

        fig_bills_treemap.update_layout(
            title={
                'text': 'Grouped Expenses',
                'x': 0
            },
        )

        # Show plot        
        st.plotly_chart(fig_bills_treemap)
    
    col1, col2, col3, col4 = st.columns([1.3, 1.5, 0.81, 1.5])

    # Investment cumulative line chart
    with col1:
        
        # Create investment dataset
        df_investment = df_date_filtered[df_date_filtered['category'] == 'Investment']
        df_investment_monthly = df_investment.sort_values(['year', 'month'])
        df_investment_monthly['cumulative_value'] = df_investment_monthly.groupby('subcategory')['value'].cumsum()

        # Create line chart
        fig_investment_cumulative = px.line(
            df_investment_monthly, 
            x = 'month_year', 
            y = 'cumulative_value', 
            color = 'subcategory',
            color_discrete_sequence = px.colors.qualitative.Pastel
        )
        
        fig_investment_cumulative.update_traces(
            hovertemplate = '<br>'.join([
                'Date: %{x}',
                'Cumulative Value: %{y:.2f}',
                'Subcategory: %{fullData.name}'
            ])
        )
        
        fig_investment_cumulative.update_layout(
            width = 430,
            title = {
                'text': '',
                'x': 0
            },
            xaxis = dict(
                title = None,
                tickangle = 360,
                tickfont_size = 13,
                nticks = 5,
            ),
            yaxis = dict(
                title = 'Amount',
                titlefont_size = 16,
                tickfont_size = 14,
                showgrid = True
            ),
            legend = dict(
                orientation = 'h',
                title = '',
                x = 0.2,
                y = 1.1,
                bgcolor = 'rgba(255, 255, 255, 0)',
                bordercolor = 'rgba(255, 255, 255, 0)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',  
            # paper_bgcolor='rgba(0,0,0,0)'  
        )
        
        st.plotly_chart(fig_investment_cumulative)
    
    # Summary statistics investment
    with col2:
        
        total_investment = df_investment['value'].sum()
        average_investment = df_investment.groupby(['month', 'year'])['value'].sum().mean()
        max_investment = df_investment_monthly['value'].max()
        max_investment_index = df_investment_monthly['value'].idxmax()
        max_investment_month = pd.to_datetime(df_investment_monthly.loc[max_investment_index, 'month_year']).strftime('%B %Y')
        min_investment = df_investment_monthly['value'].min()
        average_income_monthly = df_income_monthly['value'].mean()
        average_expenses_monthly = df_expenses_monthly['value'].mean()
        highest_expense_category = df_date_filtered_expenses.groupby('category')['value'].sum().idxmax()
        highest_income_category = df_income.groupby('category')['value'].sum().idxmax()

        summary_one = f"""
            <style>
            .center_one {{
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
                align-items: flex-start;
                height: 400px;
            }}
            p.a {{
                font: 14px/20px Georgia, serif;
                text-align: left;
                padding-left: 35px;
            }}
            h4 {{
                text-align: left;
                color: gray;
                padding-left: 35px;
            }}
            </style>
            <div class="center_one">
                <h4>Your investments</h4>
                <p class="a">The total investment from <i>{filter_date[0].strftime('%B %Y')}</i> to <i>{filter_date[1].strftime('%B %Y')}</i> was U$ <b>{total_investment:.2f}</b>.
                In average, U$ {average_investment:.2f} were saved <i>monthly</i>.
                This represents <b>{(average_investment / average_income_monthly) * 100:.2f}%</b> of your average monthly income (U$ {average_income_monthly:.2f}). 
                Most of your income comes from the 
                category <b>{highest_income_category}</b>. 
                Highest investment value was U$ {max_investment:.2f} 
                in <i>{max_investment_month}</i>.</p> 
            </div>
        """

        st.markdown(summary_one, unsafe_allow_html=True)

    # Highest expense subcategory donut chart
    with col3:

        st.markdown("""
            <style>
            .st-emotion-cache-12w0qpk.e1f1d6gn1 {
                display: flex;
                justify-content: center;
                align-items: center;
            }
            </style>
        """, unsafe_allow_html=True)

        df_highest_expense_category = df_date_filtered_expenses[df_date_filtered_expenses['category'] == highest_expense_category]
        df_expenses_donut_chart = df_highest_expense_category.groupby('subcategory')['value'].sum().reset_index()

        fig_expenses_donut_chart = px.pie(
            df_expenses_donut_chart, 
            values='value', 
            names='subcategory',
            color_discrete_sequence = px.colors.qualitative.Pastel,
            hole = 0.65,
        )

        fig_expenses_donut_chart.update_traces(
            hovertemplate="<br>".join([
                "Subcategory: %{label}",
                "Value: %{value:.2f}"
            ])
        )

        fig_expenses_donut_chart.update_layout(
            width = 250,
            title = {
                'text': '',
                'x': 0.5,
                'xanchor': 'center'
            },
            legend = dict(
                orientation = 'h',
                xanchor = 'center',
                title = '',
                x = 0.5,
                y = 0.05,
                bgcolor = 'rgba(255, 255, 255, 0)',
                bordercolor = 'rgba(255, 255, 255, 0)'
            ),
            annotations=[
                dict(
                    x = 0.5,
                    y = 0.5,
                    showarrow = False,
                    text = highest_expense_category,
                    xref = 'paper',
                    yref = 'paper',
                    font = dict(
                    size = 20
                    )
                )
            ],
            margin = dict(
                l = 0,
                r = 0
                
            )
        )

        st.plotly_chart(fig_expenses_donut_chart)

    # Expenses summary
    with col4:

        average_df_expenses_monthly_highest = df_date_filtered_expenses[df_date_filtered_expenses['category'] == highest_expense_category]
        average_df_expenses_monthly_highest = average_df_expenses_monthly_highest.groupby(['month', 'year'])['value'].sum().mean()
        

        summary_two = f"""
            <style>
            .center_two {{
                display: flex;
                flex-direction: column;
                justify-content: flex-end;
                align-items: flex-end;
                height: 400px;
            }}
            p.b {{
                font: 14px/20px Georgia, serif;
                text-align: right;
                padding-left: 35px;
            }}
            h5 {{
                text-align: left;
                color: gray;
                padding-left: 35px;
            }}
            </style>
            <div class="center_two">
                <h5 style = "text-align: right;">Understanding your expenses</h5>
                <p class="b"> Your average expenses (without considering your investments), compromised 
                    <b>{((average_expenses_monthly - average_investment) / average_income_monthly) * 100:.2f}% </b> of your monthly income
                    . The category with highest expenses is <b>{highest_expense_category}</b>, with a total of 
                    U$ {df_date_filtered_expenses.groupby('category')['value'].sum().max():.2f}. 
                    The average value spent on this category is U$ {average_df_expenses_monthly_highest:.2f} 
                    (<b>{(average_df_expenses_monthly_highest / average_income_monthly) * 100:.2f}% </b> of your budget).</p>
                     </p>
                </div>
            """        

        st.markdown(summary_two, unsafe_allow_html=True)

    st.sidebar.write("You are seeing data from", filter_date[0].strftime('%b-%Y'), "to", 
                     filter_date[1].strftime('%b-%Y'))
    
# Footer
st.markdown(footer, unsafe_allow_html=True)
