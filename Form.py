import streamlit as st
import pandas as pd
import pyperclip3

st.set_page_config(page_title = "Phyto",layout="wide")

#intro text
st.title("Welcome to Phyto")

st.write("Hi friend! I'm Phyto.\n"
         " My job is to come up with an education plan that works for you.\n"
         " All you have to do is spend 7 minutes answering some questions about your current knowledge, "
         "what you're interested in and your time capacity then I'll come up with a plan for you!\n")

#with st.form("Name"):
    #name = st.text_input('What is  your name?')
    #name = " " + name
    #name_submitted = st.form_submit_button("Submit")

st.write("In our plans **learnings can be broken down into 5 categories:** \n"
         "- **Climate background** - This category contains information on wider climate science & climate agreements\n"
         "- **Carbon markets** - This category contains information about how carbon markets work and the players within them\n"
         "- **CDR Pathways** - This category contains information about how carbon removal occurs and how it can be measured\n"
         "- **CDR Policy** - This category contains information related to CDR legislation & regulations\n"
         "- **CDR concepts** - This category contains core ideas and definitions that are key for your understanding of climate and CDR")

#titles of form
subheader = '<p style="font-family:Courier; font-size: 20px;">'
header = '<p style="font-family:Courier; font-size: 30px;">'

#create lists of questions
resources_df = pd.read_csv('meta.csv')
topics = ['CDR concepts',
          'Climate change & core science',
          'Carbon markets',
          'CDR pathways',
          'Policy']
times = [12, 8, 6, 4, 2]

#add overall priority to df
resources_df["Priority_overall"] = resources_df.reset_index().index
all_quest = []
quest_dict = pd.Series(resources_df.Question.values, index=resources_df.index).to_dict()

#get topic rankings
for a in topics:
    #get rankings for topics
    # get all resources in a given topic
    topic_list = resources_df.loc[resources_df.Topic== a, 'Priority_topic'].tolist()
    #index ranking by topic of resources
    topic_ranking_list = [b for b, _ in enumerate(topic_list)]
    #add to column priority topic the ranking
    resources_df.loc[resources_df.Topic == a, 'Priority_topic'] = topic_ranking_list

    #get list of rows with questions (remove nan), sorted by topic
    filtered = resources_df.loc[resources_df.Topic== a, 'Question'].dropna()
    all_quest.append(filtered.index.tolist())

answered = resources_df

#write form
with st.form("questions"):
    c = 0
    st.markdown(header + "Knowledge" + '</p>', unsafe_allow_html=True)
    st.write("Let's understand what you currently know")
    for category in all_quest:
        st.markdown(subheader + topics[c] + '</p>', unsafe_allow_html=True)
        c = c + 1
        for d in category:
            d = st.checkbox(quest_dict[d], key=str(d), value=False)
    st.markdown(header + "Time Capacity" + '</p>', unsafe_allow_html=True)
    month = st.selectbox("How many hours do you have to spend per month?", times)
    knowl_submitted = st.form_submit_button("I'm ready!")


vis_df = resources_df
vis_df["Known"] = ""
vis_df["Completed?"] = ""

def show_df(df, f):
    df = df[["Name", "Brief", "Completed?", "Topic", "Time_minutes", "URL"]]
    df.rename(columns={"Time_minutes": "Time (minutes)"})
    st.data_editor(
        df,
        column_config={
            "Completed?": st.column_config.CheckboxColumn("Completed?", default=False),
            "URL": st.column_config.LinkColumn("URL", max_chars=15)
        },
        hide_index=True,
    )
    if st.button("Copy to clipboard", key=h):
        pyperclip.copy(df)

if knowl_submitted == True:
    for category in all_quest:
        for d in category:
            if st.session_state[d] == True:
                vis_df.iat[d,9] = "True"

    vis_df = vis_df.drop(vis_df[vis_df['Known'] == 'True'].index)
    vis_df['cumulative'] = answered['Time_minutes'].cumsum()
    g = vis_df.shape[0]
    total_time = vis_df['cumulative'].iloc[-1]
    capacity = month*60
    iteration = int((total_time//month))
    new_index = 0

    st.markdown(header + "Here's your plan!" + '</p>', unsafe_allow_html=True)
    for f in range(10):
        old_index = new_index
        new_index = vis_df['cumulative'].sub(capacity).abs().idxmin()
        capacity = capacity + capacity
        sectioned = vis_df.iloc[old_index:new_index]
        if not sectioned.empty:
            st.markdown(subheader + "Month " +str(f+1)+ '</p>', unsafe_allow_html=True)
            h = f + g
            show_df(sectioned, h)
