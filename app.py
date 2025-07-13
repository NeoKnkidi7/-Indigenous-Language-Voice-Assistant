import streamlit as st
from gtts import gTTS
import pandas as pd
import numpy as np
import plotly.express as px
import os
import tempfile

# App configuration
st.set_page_config(
    page_title="Indigenous Language Voice Assistant",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional UI
st.markdown("""
<style>
    :root {
        --primary: #2c5f2d;
        --secondary: #97bc62;
        --accent: #2c5f2d;
        --background: #f0f7f4;
        --card: #ffffff;
        --text: #1e3d36;
        --highlight: #ffb81c;
    }
    
    .main {background-color: var(--background);}
    .st-bb {background-color: var(--card);}
    .header {color: var(--primary); font-weight: 700;}
    .subheader {color: var(--secondary);}
    .metric-card {border-radius: 10px; padding: 20px; background: var(--card); 
                box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 20px;
                border-left: 4px solid var(--primary);}
    .stButton>button {background-color: var(--primary); color: white; border-radius: 8px; padding: 8px 16px;}
    .stButton>button:hover {background-color: var(--secondary);}
    .stTabs [data-baseweb="tab-list"] {gap: 10px;}
    .stTabs [data-baseweb="tab"] {padding: 10px 20px; border-radius: 8px 8px 0 0; background: #e8f5e9;}
    .stTabs [aria-selected="true"] {background-color: var(--primary); color: white;}
    .language-badge {padding: 5px 15px; border-radius: 20px; font-weight: bold;}
    .zulu-badge {background-color: #ffd54f; color: #1e3d36;}
    .tswana-badge {background-color: #4fc3f7; color: #1e3d36;}
    .response-card {background-color: #e8f5e9; padding: 20px; border-radius: 10px; margin: 15px 0;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation' not in st.session_state:
    st.session_state.conversation = []
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = "Zulu"
if 'audio_response' not in st.session_state:
    st.session_state.audio_response = None
if 'domain' not in st.session_state:
    st.session_state.domain = "Healthcare"
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Load language resources
LANGUAGE_RESOURCES = {
    "Zulu": {
        "greeting": "Sawubona! Ngingakusiza ngani namuhla?",
        "agriculture": {
            "pests": "Ukulwa nezinambuzane, sebenzisa i-organic pesticide. Hlola izitshalo nsuku zonke.",
            "planting": "Isikhathi esihle sokutshala u-September kuya ku-October emaphandleni aseNingizimu Afrika.",
            "soil": "Hlola umhlabathi wakho ngonyaka. Geza ngomquba wemvelo ukuze uthuthukise isimo somhlabathi.",
            "water": "Qinisekisa ukuthi izitshalo zakho zithola amanzi anele, ikakhulukazi ehlobo."
        },
        "healthcare": {
            "symptoms": "Uma unezimpawu ezingajwayelekile, xhumana nogoti wezempilo ngokushesha.",
            "medication": "Ungaphuze umuthi ngaphandle kokweluleka kudokotela.",
            "hygiene": "Geza izandla zakho qhaba ngesikhathi eside ukuze uvimbele ukusakazeka kwegciwane.",
            "nutrition": "Idla ukudla okunomsoco okuhlanganisa imifino, izithelo kanye namaprotheni."
        }
    },
    "Tswana": {
        "greeting": "Dumela! O ka thusa jang kajeno?",
        "agriculture": {
            "pests": "Go lwa le disenyi, dirisa di-pesticide tsa tlhago. Sekaseka dimela letsatsi le letsatsi.",
            "planting": "Nako e e siameng go jala ke September go ya go October mo mafelong a Aforika Borwa.",
            "soil": "Sekaseka mmu wa gago ngwaga le ngwaga. O ka dirisa motswako wa tlhago go tokafatsa mmu.",
            "water": "Netefatsa gore dimela tsa gago di na le metsi a lekaneng, bogolo segologolo mo marung."
        },
        "healthcare": {
            "symptoms": "Fa o na le matshwao a a sa tlwaelegang, ikopanye le moapei wa tsa boitekanelo ka bonako.",
            "medication": "O se ka wa nwa ditlhare ntle le go laola ngaka.",
            "hygiene": "Hlatswa diatla tsa gago ka nako e telele go thibela phetiso ya diruiwa.",
            "nutrition": "Ja dijo tse di nonneng tse di akaretsang merogo, maungo le diprotein."
        }
    }
}

# Generate audio response with correct language codes
def generate_audio_response(text, language):
    try:
        # Correct language codes: Zulu = 'zu', Tswana = 'tn' (not 'ts' as sometimes documented)
        lang_code = "zu" if language == "Zulu" else "tn"
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            audio_bytes = tmp.read()
        
        return audio_bytes
    except Exception as e:
        st.error(f"Audio generation failed: {str(e)}")
        return None

# App layout
st.title("🗣️ Indigenous Language Voice Assistant")
st.markdown("""
**Bridging the digital divide for Zulu and Tswana speakers through voice technology**  
*Powered by Google Text-to-Speech and NWU Language Lab*
""")
st.divider()

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Flag_of_South_Africa.svg/1200px-Flag_of_South_Africa.svg.png", width=100)
    st.header("⚙️ Configuration")
    
    st.session_state.selected_language = st.radio(
        "Select Language",
        ["Zulu", "Tswana"],
        index=0 if st.session_state.selected_language == "Zulu" else 1
    )
    
    st.session_state.domain = st.radio(
        "Application Domain",
        ["Healthcare", "Agriculture"],
        index=0 if st.session_state.domain == "Healthcare" else 1
    )
    
    st.divider()
    st.markdown("""
    **Technology Stack:**
    - Google Text-to-Speech
    - NWU Language Lab Resources
    - Streamlit Web Framework
    """)
    
    st.divider()
    st.markdown("""
    **Supported Features:**
    - Text-based interaction
    - Agricultural advisory
    - Healthcare information
    - Multilingual responses
    - Audio responses
    """)
    
    st.divider()
    st.markdown("""
    *Developed with ❤️ for South African communities*  
    *v2.1 | © 2023 Language Access Initiative*
    """)

# Main content tabs
tab1, tab2, tab3 = st.tabs(["Text Assistant", "Language Resources", "Usage Analytics"])

with tab1:
    st.subheader(f"{st.session_state.selected_language} Text Assistant")
    st.markdown(f"<div class='language-badge {st.session_state.selected_language.lower()}-badge'>{st.session_state.selected_language} Mode • {st.session_state.domain}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Text input section
        st.markdown("### 💬 Text Input")
        st.caption("Type your query in your indigenous language")
        
        user_input = st.text_area("Your message:", value=st.session_state.user_input, height=100)
        submit_button = st.button("Submit")
        
        if submit_button and user_input:
            st.session_state.user_input = user_input
            
            # Process query
            domain_key = st.session_state.domain.lower()
            lang_data = LANGUAGE_RESOURCES[st.session_state.selected_language]
            
            # Enhanced intent recognition with multiple keywords
            user_text = user_input.lower()
            response = lang_data['greeting']
            
            # Agriculture intents
            if any(word in user_text for word in ["pest", "insect", "bug", "zinambuzane", "disenyi"]):
                response = lang_data[domain_key]['pests']
            elif any(word in user_text for word in ["plant", "grow", "seed", "tshala", "jala"]):
                response = lang_data[domain_key]['planting']
            elif any(word in user_text for word in ["soil", "dirt", "earth", "umhlabathi", "mmu"]):
                response = lang_data[domain_key]['soil']
            elif any(word in user_text for word in ["water", "irrigate", "rain", "amanzi", "metsi"]):
                response = lang_data[domain_key]['water']
                
            # Healthcare intents
            elif any(word in user_text for word in ["symptom", "pain", "fever", "impawu", "matshwao"]):
                response = lang_data[domain_key]['symptoms']
            elif any(word in user_text for word in ["medic", "pill", "drug", "umuthi", "dithlare"]):
                response = lang_data[domain_key]['medication']
            elif any(word in user_text for word in ["hygiene", "clean", "wash", "hlanza", "hlatswa"]):
                response = lang_data[domain_key]['hygiene']
            elif any(word in user_text for word in ["nutrition", "food", "diet", "ukudla", "dijo"]):
                response = lang_data[domain_key]['nutrition']
            
            st.session_state.conversation.append({
                "speaker": "User",
                "text": user_input
            })
            
            st.session_state.conversation.append({
                "speaker": "Assistant",
                "text": response
            })
            
            # Generate audio response
            st.session_state.audio_response = generate_audio_response(
                response, 
                st.session_state.selected_language
            )
            st.rerun()
        
        # Display conversation
        st.markdown("### 📝 Conversation History")
        if st.session_state.conversation:
            for msg in st.session_state.conversation:
                speaker = "👤 You" if msg['speaker'] == "User" else "🤖 Assistant"
                st.markdown(f"**{speaker}:** {msg['text']}")
                st.divider()
        else:
            st.info("No conversation yet. Submit a query to start!")
    
    with col2:
        # Response section
        st.markdown("### 🔊 Audio Response")
        
        # Audio playback
        if st.session_state.audio_response:
            st.audio(st.session_state.audio_response, format="audio/mp3")
            st.download_button(
                label="Download Response",
                data=st.session_state.audio_response,
                file_name=f"{st.session_state.selected_language}_response.mp3",
                mime="audio/mp3"
            )
        else:
            st.info("Submit a query to generate an audio response")
        
        # Domain-specific quick actions
        st.markdown("### ⚡ Quick Actions")
        domain_key = st.session_state.domain.lower()
        
        if st.button(f"Ask about {domain_key} tips"):
            response = LANGUAGE_RESOURCES[st.session_state.selected_language][domain_key]['pests']
            st.session_state.conversation.append({
                "speaker": "Assistant",
                "text": response
            })
            st.session_state.audio_response = generate_audio_response(
                response, 
                st.session_state.selected_language
            )
            st.rerun()
            
        if st.button("Request greeting"):
            response = LANGUAGE_RESOURCES[st.session_state.selected_language]['greeting']
            st.session_state.conversation.append({
                "speaker": "Assistant",
                "text": response
            })
            st.session_state.audio_response = generate_audio_response(
                response, 
                st.session_state.selected_language
            )
            st.rerun()
            
        if st.button("Clear Conversation"):
            st.session_state.conversation = []
            st.session_state.audio_response = None
            st.session_state.user_input = ""
            st.rerun()

with tab2:
    st.subheader("Language Resources")
    st.markdown("""
    ### 📚 Indigenous Language Support
    Explore resources for Zulu and Tswana languages
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### isiZulu Resources")
        st.markdown("""
        - **Common Phrases:**
          - Hello: Sawubona
          - Thank you: Ngiyabonga
          - How are you?: Unjani?
          - Goodbye: Hamba kahle
          - Please: Ngiyacela
        
        - **Agriculture Terms:**
          - Soil: Umhlabathi
          - Crops: Izitshalo
          - Harvest: Isivuno
          - Rain: Imvula
          - Seeds: Imbewu
        
        - **Healthcare Terms:**
          - Doctor: Udokotela
          - Medicine: Umuthi
          - Symptoms: Izimpawu
          - Hospital: Isibhedlela
          - Health: Impilo
        """)
        
        st.markdown("#### Learning Materials")
        st.markdown("""
        - [Zulu Grammar Guide](https://example.com)
        - [Zulu-English Dictionary](https://example.com)
        - [Cultural Resources](https://example.com)
        """)
    
    with col2:
        st.markdown("#### Setswana Resources")
        st.markdown("""
        - **Common Phrases:**
          - Hello: Dumela
          - Thank you: Ke a leboga
          - How are you?: O tsogile jang?
          - Goodbye: Tsamaya sentle
          - Please: Ka kopo
        
        - **Agriculture Terms:**
          - Soil: Mmu
          - Crops: Dimerela
          - Harvest: Go roba
          - Rain: Pula
          - Seeds: Peo
        
        - **Healthcare Terms:**
          - Doctor: Ngaka
          - Medicine: Dithlare
          - Symptoms: Matshwao
          - Hospital: Sephatlhe
          - Health: Boitekanelo
        """)
        
        st.markdown("#### Learning Materials")
        st.markdown("""
        - [Tswana Grammar Guide](https://example.com)
        - [Tswana-English Dictionary](https://example.com)
        - [Cultural Resources](https://example.com)
        """)
    
    st.divider()
    st.subheader("Community Contributions")
    st.markdown("""
    ### 👥 Join Our Community
    Help us improve our language resources:
    """)
    
    with st.form("contribution_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Email")
        language = st.selectbox("Language", ["Zulu", "Tswana"])
        contribution = st.text_area("Contribution (phrase, translation, or resource)")
        
        submitted = st.form_submit_button("Submit Contribution")
        if submitted:
            st.success("Thank you for your contribution! Our language team will review it.")

with tab3:
    st.subheader("Usage Analytics")
    st.markdown("""
    ### 📊 Adoption Metrics
    Track the impact of our indigenous language technology
    """)
    
    # Generate mock analytics data
    languages = ["Zulu", "Tswana", "Zulu", "Tswana", "Zulu", "Tswana", "Zulu"]
    domains = ["Healthcare", "Agriculture", "Healthcare", "Agriculture", "Healthcare", "Agriculture", "Healthcare"]
    regions = ["KwaZulu-Natal", "North West", "Gauteng", "Limpopo", "Eastern Cape", "Free State", "Western Cape"]
    usage = [150, 95, 120, 85, 140, 90, 130]
    
    analytics_df = pd.DataFrame({
        "Language": languages,
        "Domain": domains,
        "Region": regions,
        "Usage": usage
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Language Distribution")
        lang_counts = analytics_df["Language"].value_counts().reset_index()
        fig1 = px.pie(
            lang_counts, 
            names="Language", 
            values="count",
            color="Language",
            color_discrete_map={"Zulu": "#FFD54F", "Tswana": "#4FC3F7"},
            hole=0.3
        )
        fig1.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("#### Regional Adoption")
        region_counts = analytics_df.groupby("Region")["Usage"].sum().reset_index()
        fig2 = px.bar(
            region_counts, 
            x="Region", 
            y="Usage",
            color="Region",
            title="Usage by Region",
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        st.markdown("#### Domain Usage")
        domain_counts = analytics_df["Domain"].value_counts().reset_index()
        fig3 = px.pie(
            domain_counts, 
            names="Domain", 
            values="count",
            color="Domain",
            color_discrete_sequence=["#2c5f2d", "#97bc62"],
            title="Usage by Application Domain",
            hole=0.3
        )
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig3, use_container_width=True)
        
        st.markdown("#### Monthly Growth")
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        zulu_growth = [80, 110, 150, 190, 240, 300]
        tswana_growth = [50, 75, 110, 150, 190, 240]
        
        fig4 = px.line(
            x=months,
            y=[zulu_growth, tswana_growth],
            title="Monthly Active Users",
            labels={"x": "Month", "value": "Users"},
            color_discrete_sequence=["#FFD54F", "#4FC3F7"]
        )
        fig4.update_layout(
            showlegend=True,
            yaxis_title="Users",
            xaxis_title="Month",
            height=400
        )
        fig4.data[0].name = "Zulu"
        fig4.data[1].name = "Tswana"
        st.plotly_chart(fig4, use_container_width=True)

# Footer
st.divider()
st.markdown("""
<div style="text-align:center; color:#6c757d; font-size:0.9em; padding:20px;">
    Indigenous Language Voice Assistant v2.1 | 
    <a href="#" style="color:#2c5f2d;">Privacy Policy</a> | 
    <a href="#" style="color:#2c5f2d;">Research Methodology</a> | 
    <a href="#" style="color:#2c5f2d;">Community Guidelines</a>
</div>
""", unsafe_allow_html=True)
