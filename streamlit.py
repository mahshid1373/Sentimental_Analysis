import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from PIL import Image
from streamlit_function import *
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder

# Title of the Streamlit app
# st.title("Twitter Sentiment Analyzer")




#################################################################################################################################
########################################################### Sidebar #############################################################
#################################################################################################################################

# Sidebar for input parameters
st.sidebar.title("Twitter Sentiment Analyzer")
st.sidebar.markdown("""
This app performs sentiment analysis on the tweets based on the entered search term. 
Since the app can only predict positive or negative or neutral sentiment. Only English tweets 
are supported.
""")

# Add a horizontal line
st.sidebar.markdown("---")

st.sidebar.subheader("Please Upload your data here:")


# Upload box for users to upload their own data
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded file into a DataFrame
    df = pd.read_csv(uploaded_file)
else :
    # Upload data for demonstration purposes
    df = pd.read_csv("Data/sentimental_data.csv")
    main_df = df


st.sidebar.markdown("Note: it may take a while to load the results, especially with a large number of tweets.")

# Add a horizontal line
st.sidebar.markdown("---")

# Add a link at the bottom
st.sidebar.markdown("[Github link](https://github.com/mahshid1373)", unsafe_allow_html=True)
st.sidebar.markdown("[Linkdin link](https://www.linkedin.com/in/mahshidkhatami-data-analyst/)", unsafe_allow_html=True)

# Add "Created by" text
st.sidebar.markdown("Created by Mahshid Khatami")


#################################################################################################################################
########################################################### Tabs #############################################################
#################################################################################################################################

# Create tabs
tab1, tab2, tab3 = st.tabs(["🧮 Sentiment Analyze 🧮", "🗂 Download Clean Data 🗂", "🪛 Apply ML Models On Data 🪛"])


# Content for Tab 2
with tab2:
    st.header("Data Cleaning and Preprocessing")

    import streamlit as st

    st.markdown("""

    To prepare the text data for analysis, the following steps are applied:

    #### 1. Text Cleaning:
    - **Lowercase Conversion**: Converts all text to lowercase.
    - **Remove Brackets and Links**: Strips text in square brackets and removes URLs.
    - **Remove HTML Tags**: Eliminates any HTML elements.
    - **Punctuation Removal**: Removes all punctuation marks.
    - **Remove Newlines and Words with Numbers**: Cleans up newlines and words containing numbers.

    #### 2. Text Preprocessing:
    - **Tokenization**: Splits the text into individual words.
    - **Combine Tokens**: Joins the words back into a clean string.

    This ensures the text is ready for analysis by removing noise and standardizing the format.
    """)

    cleaned_data = clean_data(df)

    # Convert the DataFrame to CSV
    csv = cleaned_data.to_csv(index=False)

    # Add a horizontal line
    st.markdown("---")

    st.write("The preview of your cleaned Data:")

    st.dataframe(
        cleaned_data[["sentiment", "text"]].style.applymap(
            sentiment_color, subset=["sentiment"]
        ),
        height=350
    )

    st.write("Here is your cleaned Data that you can download as a CSV file.")

    # Provide a download button for the CSV file
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='cleaned_data.csv',
        mime='text/csv',
    )

# Content for Tab 3
with tab3:

    # Title for the app
    st.title("XGBoost Model Prediction")

    # Explanation
    st.markdown("""
    ### What is XGBoost?
    XGBoost, short for **Extreme Gradient Boosting**, is a powerful and efficient open-source machine learning algorithm. It belongs to the family of gradient boosting techniques, which combine the predictions of several weaker models to produce a strong predictive model.

    XGBoost is widely used in data science competitions and industry applications due to its high performance and scalability. The algorithm is particularly effective for structured/tabular data and excels in tasks like classification, regression, and ranking.

    Key features of XGBoost include:
    - **Regularization:** Helps prevent overfitting by adding penalties to the model complexity.
    - **Handling Missing Data:** Automatically learns which missing values should be treated as a separate category.
    - **Parallel Processing:** Optimizes computational resources by performing operations in parallel.

    In this application, we utilize XGBoost to make predictions based on your data, leveraging its capabilities to deliver accurate and reliable results.
    """)

    st.write("Preview of Uploaded Test Data:")
    st.dataframe(
        df[["text"]],
        height=350
    )

    cleaned_data = clean_data(df)

    # Initialize the LabelEncoder
    label_encoder = LabelEncoder()

    # Fit and transform the data
    cleaned_data['sentiment'] = label_encoder.fit_transform(cleaned_data['sentiment'])


    cleaned_data_feature = cleaned_data["text"]

    # Load the vectorizer and the trained XGBoost model from the .pkl file
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    model_filename = 'xgboost_model.pkl'
    with open(model_filename, 'rb') as file:
        model = pickle.load(file)

    X_test_vect = vectorizer.transform(cleaned_data_feature)

    predictions = model.predict(X_test_vect)

    # Display the predictions
    st.subheader("Predictions")
    
    cleaned_data['Prediction'] = predictions    

    # New Markdown
    st.markdown("""
    These are the value means as sentiment:

    - **Negative : 0**
    - **Neutral : 1**
    - **Positive : 2**
    """)

    # Display the predictions
    cleaned_data['Prediction'] = predictions
    # st.dataframe(cleaned_data)
    st.dataframe(
    cleaned_data[["Prediction", "text"]].style.applymap(
        sentiment_color, subset=["Prediction"]
    ),
    height=350
    )
    
    # Optionally, allow users to download the results
    st.write("Download The Prediction of Uploaded Test Data:")
    csv = cleaned_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Predictions as CSV",
        data=csv,
        file_name='predictions.csv',
        mime='text/csv',
    )


# Content for Tab 1
with tab1:
    #################################################################################################################################
    ############################################################# Layout ########################################################
    #################################################################################################################################

    # Layout
    st.header("Sentiment Analysis Results")

    ########################################### Pie Chart ##########################################################
    # Sentiment Distribution 
    sentiment_count = df['sentiment'].value_counts()
    # Define custom colors
    warm_colors = ['#FF7F0E', '#FFBB78', '#FF4136']  # Example warm colors: orange, light orange, red
    fig_pie = px.pie(values=sentiment_count, 
                    names=sentiment_count.index, 
                    title="Sentiment Distribution",
                    color_discrete_sequence=warm_colors
                    )

    ########################################### Top 10 Occurring Words Bar Chart ###################################################
    df['text'] = df['text'].astype(str)
    word_freq = pd.Series(' '.join(df['text']).lower().split()).value_counts()[:10]
    fig_bar = px.bar(x=word_freq.values, 
                    y=word_freq.index, 
                    orientation='h', 
                    labels={'x': 'Frequency', 'y': 'Words'},  # Adding x and y labels
                    title="Top 10 Occurring Words",
                    color_discrete_sequence=warm_colors
                    )


    ########################################### bigrams ##########################################################
    vectorizer = CountVectorizer(ngram_range=(2, 2))  # Set ngram_range to (2, 2) for bigrams
    X = vectorizer.fit_transform(df['text'])
    bigrams = vectorizer.get_feature_names_out()
    freqs = X.sum(axis=0).A1
    bigram_freq = pd.DataFrame({'Bigram': bigrams, 'Frequency': freqs})

    # Sort by frequency and get the top 10
    top_bigrams = bigram_freq.sort_values(by='Frequency', ascending=False).head(10)

    # Create the bar chart
    fig_bigram = px.bar(top_bigrams, x='Frequency', y='Bigram', orientation='h', title="Top 10 Occurring Bigrams",
                    color_discrete_sequence= warm_colors)  # Optional: Set a specific color

    ########################################### First Row ##########################################################

    # Use st.columns to place both plots in the same row
    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(fig_pie)

    with col2:
        st.plotly_chart(fig_bar)

    with col3:
        st.plotly_chart(fig_bigram)



    ########################################### Word Cloud ##########################################################
    # Load the Twitter logo image
    twitter_mask = np.array(Image.open("Figures/Logo_Twitter.png"))


    # Generate the word cloud
    wordcloud = WordCloud(
        mask=twitter_mask, 
        colormap='Oranges'  # Use a warm color map to match the color scheme
    ).generate(' '.join(df['text']))

    # Plot the word cloud
    plt.imshow(wordcloud, interpolation='bilinear')

    # Save and display the word cloud in Streamlit
    plt.savefig('Figures/wordcloud_twitter.png', format="png", transparent=True, bbox_inches='tight')



    ########################################### Second Row ##########################################################

    col1, col2 = st.columns([60, 40])

    with col1:
        st.subheader("Sample Tweets")
        # show the dataframe containing the tweets and their sentiment
        st.dataframe(
            df[["sentiment", "text"]].style.applymap(
                sentiment_color, subset=["sentiment"]
            ),
            height=350
        )

    with col2:
        st.subheader("Word Cloud")
        st.image('Figures/wordcloud_twitter.png', caption="Word Cloud")



