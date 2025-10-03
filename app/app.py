from turtle import width
from pathlib import Path
import streamlit as st
import pandas as pd
import os
import io

# pip install streamlit pandas openpyxl

# layout a nadpis
st.set_page_config(layout="wide")
st.title("🗂️ Samplesheets") # jiny ikonky tam bohuzel dat nejdou, tak tam sou tyhle hnusny

#[theme]
#base="light"
#secondaryBackgroundColor="#18b9a6"
#textColor="#111827"

# cesty
HERE = Path(__file__).resolve().parent 
ROOT = HERE.parent  
LIB_DIR = ROOT / "libraries"
HELP_DIR = ROOT / "helps"

library_path = LIB_DIR
files = [f for f in os.listdir(library_path) if f.endswith(".xlsx")]

if not files:
    st.warning("Ve složce 'libraries/' nejsou žádné Excel soubory.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Výběr indexů", "Manifest","Knihovny",])

with tab1:
    # vyber knihovny, rozbalovaci seznam a dataframe
    st.subheader("1. Vyber knihovnu a doplň názvy vzorků")
    file_selection = st.selectbox(label = "Vyber knihovnu:", options = files, label_visibility = "collapsed")
    file_path = os.path.join(library_path, file_selection)
    df_raw = pd.read_excel(file_path)

    print("*************************************************************************************************************")
    print(file_path)
    print(df_raw.head(5))


    #expander = st.expander("O knihovnách")
    #expander.write(df_info)

    # odstranit mezery u nazvu sloupcu
    df_raw.columns = [col.strip() for col in df_raw.columns]

    # pridani sloupce pro vzorky
    df = df_raw.copy()
    df.insert(0, "Sample name", "")

    # print(df_raw.head(5))

    # pretypovani sloupce index
    df["INDEX"] = df["INDEX"].astype(str)

    # rozbalovaci seznam pro vyber konkretniho indexu - 2. možnost filtru
    with st.expander("Výběr indexů", icon=":material/search:", expanded = False):
        col1, col2, col3 = st.columns(3)
        with col1:
            index = st.multiselect(label = "Filtruj podle indexu", options = [""] + sorted(df["INDEX"].unique()), key="index")
        with col2:
            i7_filter = st.multiselect(label = "Filtruj podle i7 name", options = [""] + sorted(df["i7 name"].unique()), key="i7_filter")
        with col3:
            i5_filter = st.multiselect(label = "Filtruj podle i5 name", options = [""] + sorted(df["i5 name"].unique()), key="i5_filter")

    # 🔍
    print("typy sloupců", df.dtypes)
    print("typ index:", type(index[0]) if index else "prázdný")
    print("index", index)
    print("hodnoty ve filtrech")
    print("i7_filter", i7_filter)
    print("i5_filter", i5_filter)
    print("hodnoty ve sloupcich")
    print("INDEX:", df["INDEX"].dropna().unique().tolist())
    print("i7 name:", df["i7 name"].dropna().unique().tolist())
    print("i5 name:", df["i5 name"].dropna().unique().tolist())

    # filtr pro konkretni hodnoty 
    #if index_start and index_end:
    #    filtered_df = df[(df["INDEX_num"] >= index_start) & (df["INDEX_num"] <= index_end)]
    mask = pd.Series([False] * len(df))

    if index and index != [""]:
        mask |= df["INDEX"].isin(index)
    if i7_filter and i7_filter != [""]:
        mask |= df["i7 name"].astype(str).str.strip().isin(i7_filter)
    if i5_filter and i5_filter != [""]:
        mask |= df["i5 name"].astype(str).str.strip().isin(i5_filter)

    if not mask.any():
        filtered_df = df.copy()
    else:
        filtered_df = df[mask]

    print(filtered_df.head(5))
        
    #filtered_df = filtered_df.reset_index(drop=True)

    #filtered_df[""] = ""


    ##### TAB 1

    # cela tabulka se vsim nastavenym
    st.markdown("Tabulka s indexy a vzorky")
    edited_libraries_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "Sample name": st.column_config.TextColumn("Sample name", help="Zadej nebo vlož názvy vzorků"),
            "INDEX": st.column_config.TextColumn("INDEX", width="small"),
        },
        column_order=[
            "INDEX", "Sample name", "i7 sequence", "i5 sequence", "i7 name", "i5 name"
        ]
    )

    print(edited_libraries_df)
    # 📄 
    # export
    export_libraries_df = edited_libraries_df.copy()

    # export jen tech radku, kde je nazev vzorku
    #export_libraries_df = export_libraries_df[export_libraries_df["Sample name"].astype(str).str.strip() != ""]
    export_libraries_df = export_libraries_df[
    export_libraries_df["Sample name"].notna() &  # odstraní NaN/None
    (export_libraries_df["Sample name"].astype(str).str.strip() != "")
]

    print(export_libraries_df)

    # nastaveni exportu
    if export_libraries_df.empty:
        st.info("Žádné řádky k exportu (zkontroluj filtr nebo prázdné vzorky).", icon=":material/info:")
    else:
        #st.markdown("Export výsledků")
        csv = export_libraries_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Stáhnout jako CSV",
            data=csv,
            file_name="samples.csv",
            mime="text/csv",
            type="primary"
        )
# 💬 💾 , icon=":material/file_download:"
#    st.divider()

with tab2:
    ##### TAB 2

    # hlavicka
    head_path = HELP_DIR
    #df_head = pd.read_excel(os.path.join(head_path, "head.xlsx"))

    if "df_head" not in st.session_state:
        df_head = pd.read_excel(head_path / "head.xlsx")
        st.session_state.df_head = df_head.copy()
        st.session_state.df_head.columns = ["Sample name", "Index 1", "Index 2", "Lane"]

    # pocet vzorku = pocet radku
    st.subheader("2. Zadej počet vzorků a překopíruj jejich názvy s indexy")
    #col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
    #col1, col2 = st.columns([10, 1], gap="small")
    col1, col2, col_spacer = st.columns([1, 0.6, 9])


    with col1:
        num_samples = st.number_input(" ", min_value=1, value=1, width="stretch", label_visibility="collapsed")
    with col2:
        if st.button("", icon=":material/done:", type="primary"):
            num_rows = pd.DataFrame(index=range(num_samples), columns=st.session_state.df_head.columns)
            st.session_state.df_head = pd.concat([st.session_state.df_head, num_rows], ignore_index=True).reset_index(drop=True)
            #st.session_state.df_head = st.session_state.df_head.reset_index(drop=True)
    
    #st.markdown("(1 vzorek = 1 řádek)")
            
    #st.markdown("(1 vzorek = 1 řádek)")

    df_head = st.session_state.df_head
    table_height = len(df_head)
    df_table = min(max(table_height * 35, 300), 1000)

    # cela tabulka se vsim nastavenym
    st.markdown("Tabulka s hlavičkou")
    edited_samplesheet_df = st.data_editor(
        st.session_state.df_head,
        height=df_table,
        use_container_width=True,
        hide_index=False,
        num_rows="dynamic"
    )

    print(edited_samplesheet_df)

    # kontrola lane
    valid_rows = edited_samplesheet_df.dropna(subset=["Index 1", "Index 2", "Lane"])

    #if len(edited_samplesheet_df) > 13:
        #df_lane = edited_samplesheet_df.iloc[13:].copy()
    if not valid_rows.empty:
        dups = valid_rows.duplicated(subset=["Index 1", "Index 2", "Lane"], keep=False)

        set_of_duplicates = set(
            valid_rows.loc[dups, ["Index 1", "Index 2", "Lane"]].itertuples(index=False, name=None)
        )

        def highlight_duplicates(row):
            if (row["Index 1"], row["Index 2"], row["Lane"]) in set_of_duplicates:
                return ['background-color: #ffcccc'] * len(row)
            else:
                return [''] * len(row)

        if dups.any():
            st.error("Některé vzorky mají stejný index (i7+i5) na stejné lajně! Zkontroluj prosím.", icon=":material/error:")
            styled_df = valid_rows.style.apply(highlight_duplicates, axis=1)
            st.dataframe(styled_df)

    # ⚠️ 
    #st.dataframe(styled_df)

    # export
    export_samplesheet_df = edited_samplesheet_df.copy()

    # export do xlsx
    export_samplesheet_df = edited_samplesheet_df.copy()
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        export_samplesheet_df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)

    # nastaveni exportu
    if export_samplesheet_df.empty:
        st.info("Žádné řádky k exportu (zkontroluj filtr nebo prázdné vzorky).", icon=":material/error:")
    else:
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)
        with col3: 
            st.markdown("")
            csv = export_samplesheet_df.to_csv(index=False).encode("utf-8")
        with col1:
            st.download_button(
                label="Stáhnout jako CSV",
                data=csv,
                file_name="samplesheet.csv",
                mime="text/csv",
                type="primary"
            )
        with col2:
            st.download_button(
                label="Stáhnout jako XLSX",
                data=output,
                file_name="samplesheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
# 💬 
    
with tab3:
    
    # popisy knihoven
    info_path = HELP_DIR
    file_info = info_path / "info.txt"
    #df_info = pd.read_csv(file_info, sep="\t")
    with open(file_info, "r", encoding="utf-8") as f:
        text_info = f.read().replace(";", "\n")

    with st.expander(label = "O knihovnách", icon=":material/book:", expanded = True):
        st.markdown(text_info)