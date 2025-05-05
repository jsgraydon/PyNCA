import pandas as pd
import streamlit as st
from module import pk_data


# Initialize
## Variables
if 'summ_clicked' not in st.session_state:
    st.session_state.summ_clicked = False

if 'viz_clicked' not in st.session_state:
    st.session_state.viz_clicked = False

if 'nca_clicked' not in st.session_state:
    st.session_state.nca_clicked = False

## Functions
def click_summ():
    st.session_state.summ_clicked = True

def click_viz():
    st.session_state.viz_clicked = True

def click_nca():
    st.session_state.nca_clicked = True

def click_clear():
    st.session_state.summ_clicked = False
    st.session_state.viz_clicked = False
    st.session_state.nca_clicked = False

st.logo("logo.png", size="large")

# Define GUI elements
st.title('PyNCA: Noncompartmental Analysis in Python')

upload = st.file_uploader("upload data as CSV")

if upload is not None:

    ## Read in data
    df = pd.read_csv(upload)

    pk = pk_data(df)

    st.sidebar.subheader("Data")
    ## Summarize
    #st.subheader("Summarize")
    st.sidebar.button("Summarize", on_click=click_summ, icon=":material/summarize:", key="btn1")

    if st.session_state.summ_clicked:
        st.write("Summarized PK data:")
        st.dataframe(pk.summarize())

    ## Visualize
    #st.subheader("Visualize")
    st.sidebar.button("Visualize", on_click=click_viz, icon=":material/show_chart:", key="btn2")

    summ_stats = st.sidebar.toggle("Summary level")
    log_scale = st.sidebar.toggle("Semi-log scale")


    if st.session_state.viz_clicked:
        if summ_stats:
            if log_scale:
                st.plotly_chart(pk.plot(summarized=True, log_scale=True))
            else:
                st.plotly_chart(pk.plot(summarized=True, log_scale=False))
        else:
            if log_scale:
                st.plotly_chart(pk.plot(summarized=False, log_scale=True))
            else:
                st.plotly_chart(pk.plot(summarized=False, log_scale=False))

    ## NCA
    st.sidebar.divider()
    st.sidebar.subheader("NCA")
    df = pk.summarize()
    default_start = df['TIME'].min()
    default_end = df['TIME'].max()

    slide_start = st.sidebar.slider('Select the start time for the NCA:', default_start, default_end)
    slide_end = st.sidebar.slider('Select the end time for the NCA:', default_start, default_end)

    term_times = st.sidebar.multiselect('Select times for the terminal elimination phase:', df['TIME'].tolist(), df['TIME'].tolist()[-3:])
        
    if len(term_times) != 3:
        st.write("Please select 3 timepoints for the terminal elimination phase")
    
    #st.write('Start time:', slide_start)
    #st.write('End time:', slide_end)
    #st.write("Terminal elimination times:", term_times)

    st.sidebar.button("Run NCA", on_click=click_nca, icon=":material/table:", key="btn3")

    if st.session_state.nca_clicked and len(term_times) == 3:
        st.write("Results of NCA:")
        st.dataframe(pk.report_df(term_elim_times=term_times.sort(), start=slide_start, end=slide_end))

    st.sidebar.button("Clear all results", on_click=click_clear, icon=":material/clear_all:", key="btn4")
    
