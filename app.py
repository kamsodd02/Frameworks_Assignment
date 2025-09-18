import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from collections import Counter

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    # Convert publish_time to datetime
    df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
    df["PublicationYear"] = df["publish_time"].dt.year

    # Abstract word count
    df["abstractWordCount"] = df["abstract"].astype(str).apply(lambda x: len(x.split()))

    return df

# ⚠️ Change path if needed
df = load_data("metadata_subset.csv")

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

years = sorted(df["PublicationYear"].dropna().unique())
selected_year = st.sidebar.selectbox("Select Year", options=["All"] + years)

journal_options = df["journal"].dropna().unique()
selected_journal = st.sidebar.selectbox("Select Journal", options=["All"] + list(journal_options))

source_options = df["source_x"].dropna().unique() if "source_x" in df.columns else []
selected_source = st.sidebar.selectbox("Select Source", options=["All"] + list(source_options))

# Apply filters
filtered_df = df.copy()
if selected_year != "All":
    filtered_df = filtered_df[filtered_df["PublicationYear"] == selected_year]
if selected_journal != "All":
    filtered_df = filtered_df[filtered_df["journal"] == selected_journal]
if selected_source != "All":
    filtered_df = filtered_df[filtered_df["source_x"] == selected_source]

st.sidebar.write(f"📊 Showing {len(filtered_df)} papers")

# Download button
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="filtered_metadata.csv",
    mime="text/csv",
)

# -----------------------------
# Layout: Title
# -----------------------------
st.title("📊 COVID-19 Research Dashboard")
st.write("Explore COVID-19 research papers interactively with filters and visualizations.")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📄 Data Sample",
    "ℹ️ Dataset Info",
    "📈 Publications Over Time",
    "📚 Top Journals",
    "☁️ Word Cloud",
    "📦 Sources & Word Frequency"
])

# -----------------------------
# Tab 1: Data Sample
# -----------------------------
with tab1:
    st.subheader("Sample of Filtered Data")
    st.dataframe(filtered_df.head(20))

# -----------------------------
# Tab 2: Dataset Info
# -----------------------------
with tab2:
    st.subheader("Dataset Overview")
    st.write(f"**Shape (filtered):** {filtered_df.shape[0]} rows × {filtered_df.shape[1]} columns")
    st.write("**Data Types:**")
    st.write(df.dtypes)

    # Missing values
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    st.write("**Columns with missing values:**")
    st.write(missing)

    # Descriptive stats
    st.subheader("Descriptive Statistics")
    st.write(df.describe(include="all"))

# -----------------------------
# Tab 3: Publications Over Time
# -----------------------------
with tab3:
    st.subheader("Publications Over Time")
    papers_per_year = filtered_df["PublicationYear"].value_counts().sort_index()

    if not papers_per_year.empty:
        fig, ax = plt.subplots()
        papers_per_year.plot(kind="line", marker="o", ax=ax)
        ax.set_title("Number of Publications Over Time")
        ax.set_xlabel("Year")
        ax.set_ylabel("Number of Publications")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")

# -----------------------------
# Tab 4: Top Journals
# -----------------------------
with tab4:
    st.subheader("Top 10 Journals")
    top_journals = filtered_df["journal"].value_counts().head(10)

    if not top_journals.empty:
        fig, ax = plt.subplots()
        top_journals.plot(kind="bar", color="skyblue", ax=ax)
        ax.set_title("Top Journals")
        ax.set_xlabel("Journal")
        ax.set_ylabel("Number of Publications")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(fig)
    else:
        st.warning("No journal data available for the selected filters.")

# -----------------------------
# Tab 5: Word Cloud
# -----------------------------
with tab5:
    st.subheader("Word Cloud of Paper Titles")
    all_titles = " ".join(filtered_df["title"].dropna().astype(str))

    if all_titles.strip():
        wc = WordCloud(width=800, height=400, background_color="white").generate(all_titles)
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)
    else:
        st.warning("No titles available for the selected filters.")

# -----------------------------
# Tab 6: Sources & Word Frequency
# -----------------------------
with tab6:
    if "source_x" in filtered_df.columns:
        st.subheader("Paper Counts by Source")
        source_counts = filtered_df["source_x"].value_counts()

        if not source_counts.empty:
            fig, ax = plt.subplots()
            source_counts.plot(kind="bar", color="lightgreen", ax=ax)
            ax.set_title("Distribution of Papers by Source")
            ax.set_xlabel("Source")
            ax.set_ylabel("Publications")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
        else:
            st.warning("No source data available for the selected filters.")

    # Word frequency
    st.subheader("Top 20 Frequent Words in Titles")
    words = re.findall(r"\b\w+\b", all_titles.lower())
    word_counts = Counter(words).most_common(20)
    if word_counts:
        st.write(pd.DataFrame(word_counts, columns=["Word", "Frequency"]))
    else:
        st.warning("No words available for frequency analysis.")
