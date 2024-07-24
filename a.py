import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(layout="wide")

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'apply_clicked' not in st.session_state:
    st.session_state.apply_clicked = False
if 'weights' not in st.session_state:
    st.session_state.weights = {}
if 'filtered_data' not in st.session_state:
    st.session_state.filtered_data = None

def landing_page():
    col1, col2 = st.columns([1, 1])  # Adjust the ratio as needed

    with col1:
        st.markdown(
            """
            <style>
                button[kind="secondary"][data-testid="baseButton-secondary"] {
                    margin-top: 20px;
                    width: 50%;
                    color: #FF4B4B;
                    border: 3px solid #FF4B4B;
                }

                button[kind="secondary"][data-testid="baseButton-secondary"]:hover {
                    color: white;
                    border: 3px solid white;
                }
            </style>

            <div class="header-container;">
                <div>
                    <h1 style="color: #FF4B4B;">TimKU</h1>
                    <h2>TimKU, Seleraku</h2>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Mulai"):
            st.session_state.page = 'main'

    with col2:
        st.image("7.jpeg", use_column_width=True)

def main_page():
    # Step 1: Read the data
    data = pd.read_csv('newfb2.csv')

    # Select league
    st.write("### Silahkan Pilih Liga Favorit Anda")
    league_options = data['League'].unique()
    selected_league = st.selectbox('Select a League', league_options)

    filtered_data = data[data['League'] == selected_league]

    st.markdown("<br>", unsafe_allow_html=True)

    st.write(f"### Daftar Klub yang Ada di Liga {selected_league} beserta Kriterianya (Musim 2023/2024)")
    filtered_data_display = filtered_data.reset_index(drop=True)
    filtered_data_display.index = filtered_data_display.index + 1  
    st.dataframe(filtered_data_display)

    st.markdown("<br>", unsafe_allow_html=True)

    # Criteria
    benefit_criteria = ['Possession', 'Pass', 'Defence', 'GK Save', 'Clean Sheet', 'Shot on Target', 'Assist', 'Goal']
    cost_criteria = ['Goal Against', 'Yellow Card', 'Red Card']

    # Normalize the decision matrix for SAW method
    normalized_data_saw = filtered_data.copy()
    normalized_data_saw[benefit_criteria] = filtered_data[benefit_criteria] / filtered_data[benefit_criteria].max()
    normalized_data_saw[cost_criteria] = filtered_data[cost_criteria].min() / filtered_data[cost_criteria]

    # Criteria for both SAW and TOPSIS
    criteria = benefit_criteria + cost_criteria

    # Definitions
    definitions = {
        'Possession': 'Possession adalah waktu yang dimiliki oleh tim dalam menguasai bola selama pertandingan. Semakin tinggi proporsi waktu penguasaan bola, semakin dominan tim dalam mengontrol permainan. Dengan kata lain, semakin tinggi angka Possession, semakin bagus tim tersebut dalam mengontrol bola. Dalam data ini, angka Possession ditunjukkan dalam bentuk persentase.',
        'Pass': 'Pass adalah umpan yang berhasil dilakukan oleh tim. Kemampuan dalam memberikan umpan yang akurat dan efektif memungkinkan tim untuk mengatur serangan dengan baik. Semakin tinggi angka Pass, maka semakin bagus kemungkinan serangan tim tersebut. Dalam data ini, angka Pass ditunjukkan dalam bentuk persentase.',
        'Defence': 'Defence adalah keberhasilan tim dalam mencegah serangan lawan dan menjaga area pertahanan mereka. Pertahanan yang kuat dapat membuat lawan kesulitan untuk mencetak gol. Semakin tinggi angka Defence, maka semakin bagus pertahanan tim tersebut. Dalam data ini, angka Defence ditunjukkan dalam bentuk persentase.',
        'GK Save': 'GK Save adalah penyelamatan yang berhasil dilakukan oleh penjaga gawang. Penjaga gawang yang memiliki tingkat penyelamatan yang tinggi dapat mengamankan gawang timnya dari kebobolan gol. Semakin tinggi angka GK Save, maka semakin bagus penjaga gawang tim tersebut. Dalam data ini, angka GK Save ditunjukkan dalam bentuk persentase.',
        'Clean Sheet': 'Clean Sheet adalah pertandingan di mana tim tidak kebobolan gol sama sekali. Mencatat clean sheet menunjukkan bahwa pertahanan tim sangat kuat dan sulit ditembus oleh lawan. Semakin tinggi angka Clean Sheet, maka semakin bagus pertahanan atau penjaga gawang tim tersebut. Dalam data ini, angka Chean Sheet ditunjukkan dalam bentuk persentase.',
        'Shot on Target': 'Shot on Target adalah tembakan yang mengarah tepat ke sasaran gawang lawan. Semakin tinggi proporsi tembakan yang mengarah tepat sasaran, semakin besar kemungkinan tim untuk mencetak gol. Semakin tinggi angka Shot on Target, maka semakin sering tim tersebut berpeluang mencetak gol. Dalam data ini, angka Shot on Target ditunjukkan dalam bentuk persentase.',
        'Assist': 'Assist adalah umpan terakhir yang mengarah pada gol yang dicetak oleh rekan satu tim. Memberikan assist menunjukkan kemampuan dalam memberikan kontribusi penting dalam mencetak gol.',
        'Goal': 'Goal adalah jumlah gol yang dicetak oleh tim selama pertandingan. Gol merupakan hasil akhir yang paling diharapkan dalam sepakbola dan menentukan kemenangan tim.',
        'Goal Against': 'Goal Against adalah gol yang diterima oleh tim dari serangan lawan. Kebobolan gol mengindikasikan kelemahan dalam pertahanan tim yang perlu diperbaiki.',
        'Yellow Card': 'Kartu kuning yang diterima oleh tim sebagai peringatan dari wasit terkait pelanggaran yang dilakukan. Terlalu banyak kartu kuning dapat membahayakan tim karena berpotensi mendapat kartu merah.',
        'Red Card': 'Kartu merah yang diterima oleh tim yang menunjukkan bahwa pemain tim tersebut harus dikeluarkan dari lapangan. Kartu merah dapat membuat tim bermain dengan jumlah pemain yang lebih sedikit.'
    }

    # Step 2: Input Weights
    st.write("### Pilih Kriteria Tim Sepak Bola sesuai Selera Anda")
    st.markdown("<br>", unsafe_allow_html=True)

    if 'show_definitions' not in st.session_state:
        st.session_state.show_definitions = {criterion: False for criterion in criteria}

    weights = {}
    for index, criterion in enumerate(criteria, start=1):
        st.write(f"### {index}. {criterion}")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(f"Apa itu {criterion}?", key=f"btn_{criterion}"):
            st.session_state.show_definitions[criterion] = not st.session_state.show_definitions[criterion]
        
        if st.session_state.show_definitions[criterion]:
            st.write(definitions[criterion])

        st.markdown("<br>", unsafe_allow_html=True)

        if criterion == "Goal Against":
            st.write("### Menurut Anda, apakah tim dengan jumlah kebobolan yang tinggi itu merugikan?")
            st.write("Rentang nilai 1 - 5 menunjukkan skala:")
            st.write("""
            - 1 = Tidak merugikan sama sekali
            - 2 = Sedikit merugikan
            - 3 = Biasa
            - 4 = Agak merugikan
            - 5 = Sangat merugikan""")
            unique_key = "slider_goal_against"
            weights[criterion] = st.slider("", 1, 5, 3, key=unique_key) / 5

        elif criterion == "Red Card":
            st.write("### Menurut Anda, apakah tim dengan pemain yang banyak mendapatkan kartu merah itu merugikan?")
            st.write("Rentang nilai 1 - 5 menunjukkan skala:")
            st.write("""
            - 1 = Tidak merugikan sama sekali
            - 2 = Sedikit merugikan
            - 3 = Biasa
            - 4 = Agak merugikan
            - 5 = Sangat merugikan""")
            unique_key = "slider_red_card"
            weights[criterion] = st.slider("", 1, 5, 3, key=unique_key) / 5

        elif criterion == "Yellow Card":
            st.write("### Menurut Anda, apakah tim dengan pemain yang banyak mendapatkan kartu kuning itu merugikan?")
            st.write("Rentang nilai 1 - 5 menunjukkan skala:")
            st.write("""
            - 1 = Tidak merugikan sama sekali
            - 2 = Sedikit merugikan
            - 3 = Biasa
            - 4 = Agak merugikan
            - 5 = Sangat merugikan""")
            unique_key = "slider_yellow_card"
            weights[criterion] = st.slider("", 1, 5, 3, key=unique_key) / 5

        else:
            st.write("### Menurut Anda, apakah tim dengan {} yang tinggi itu penting?".format(criterion.lower()))
            st.write("Rentang nilai 1 - 5 menunjukkan skala:")
            st.write("""
            - 1 = Sangat tidak penting
            - 2 = Tidak terlalu penting
            - 3 = Biasa
            - 4 = Agak penting
            - 5 = Sangat penting""")
            unique_key = f"slider_{criterion}"  # Membuat kunci (key) yang unik
            weights[criterion] = st.slider("", 1, 5, 3, key=unique_key) / 5

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)


    # Add the Apply button
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <style>
                button[kind="secondary"][data-testid="baseButton-secondary"] {
                    width: 100%;
                    color: white;
                    border-color: white;
                }

                button[kind="secondary"][data-testid="baseButton-secondary"]:hover {
                    color: #FF4B4B;
                    border-color: #FF4B4B;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        if st.button("Apply"):
            st.session_state.weights = weights
            st.session_state.apply_clicked = True

    with col2:
        st.markdown(
            """
            <style>
                button[kind="secondary"][data-testid="baseButton-secondary"] {
                    width: 100%;
                    color: white;
                    border-color: white;
                }

                button[kind="secondary"][data-testid="baseButton-secondary"]:hover {
                    color: #FF4B4B;
                    border-color: #FF4B4B;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        if st.button("Clear"):
            st.session_state.apply_clicked = False

    if st.session_state.apply_clicked:
        weights_series = pd.Series(st.session_state.weights)

        # Calculate the weighted normalized matrix for TOPSIS method
        weighted_normalized_data = normalized_data_saw[criteria].multiply(weights_series, axis=1)

        # Determine the positive ideal solution and the negative ideal solution
        positive_ideal_solution = weighted_normalized_data.max()
        negative_ideal_solution = weighted_normalized_data.min()

        # Determine the weighted distance of each alternative to the positive ideal solution (A^+) and the negative ideal solution (A^-)
        dist_positive = np.sqrt(((weighted_normalized_data - positive_ideal_solution) ** 2).sum(axis=1))
        dist_negative = np.sqrt(((weighted_normalized_data - negative_ideal_solution) ** 2).sum(axis=1))

        # Determine the preference value for each alternative
        topsis_scores = dist_negative / (dist_positive + dist_negative)
        filtered_data['Score'] = topsis_scores

        st.markdown("<br>", unsafe_allow_html=True)

        st.write("### Club Sesuai Seleramu adalah")
        top_club = filtered_data.sort_values(by='Score', ascending=False).iloc[0]

        top_club_name = top_club['Squad']

        st.markdown(
            f"""
            <div style="text-align: center; margin: 20px 0 20px 0">
                <h1>{top_club_name}</h1>
            </div>
            """,
            unsafe_allow_html=True
        )

        if 'show_table' not in st.session_state:
            st.session_state.show_table = False

        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Tunjukkan Hasil Club secara Keseluruhan"):
                st.session_state.show_table = True

        with col2:
            if st.button("Sembunyikan Hasil Club Keseluruhan"):
                st.session_state.show_table = False

        if st.session_state.show_table:
            st.write("### Hasil Club secara Keseluruhan")
            sorted_filtered_data = filtered_data.sort_values(by='Score', ascending=False).reset_index(drop=True)
            sorted_filtered_data.index = sorted_filtered_data.index + 1  
            st.dataframe(sorted_filtered_data)

# Render the appropriate page based on session state
if st.session_state.page == 'landing':
    landing_page()
elif st.session_state.page == 'main':
    main_page()