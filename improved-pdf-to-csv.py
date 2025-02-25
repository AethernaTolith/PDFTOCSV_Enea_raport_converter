import os
import io
import time
from datetime import timedelta
import PyPDF2
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
import pandas as pd
import csv
from stqdm import stqdm

# === Configuration ===
st.set_page_config(
    page_title="PDF to CSV Conversion",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv()

# === State Management ===
def init_session_state():
    """Initialize session state variables"""
    if "df_results" not in st.session_state:
        st.session_state.df_results = pd.DataFrame(
            columns=[
                "Podmiot",
                "Siedziba / miejsce zamieszkania",
                "Lokalizacja przyłączenia",
                "Moc przyłączeniowa [kW]",
                "Rodzaj instalacji",
                "Data wydania warunków przyłączenia",
                "Data zawarcia umowy o przyłączenie",
                "Data rozpoczęcia dostarczania energii elektrycznej",
                "Uwagi",
            ]
        )
    defaults = {
        "pdf_reader": None,
        "uploaded_file": None,
        "pdf_url": "",
        "start_page": 1,
        "end_page": 1,
        "total_pages": 1,
        "conversion_running": False,
        "stop_button_pressed": False,
        "api_key": os.environ.get("GEMINI_API_KEY", ""),
        "theme": "light",
        "language": "pl",
        "processed_pages": 0,
        "model": "gemini-2.0-flash-exp",
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize state
init_session_state()

# === Theme & Styling ===
def apply_theme():
    """Apply custom CSS based on selected theme"""
    if st.session_state.theme == "dark":
        st.markdown("""
        <style>
        .stApp {background-color: #1E1E1E}
        .sidebar .sidebar-content {background-color: #262626}
        </style>
        """, unsafe_allow_html=True)
    
    # Common styling regardless of theme
    st.markdown("""
    <style>
    .big-font {font-size:28px !important; font-weight:600; margin-bottom:15px}
    .card {
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

apply_theme()

# === API Configuration ===
def configure_api():
    """Configure the API with the given key"""
    api_key = st.session_state.api_key
    if not api_key:
        return False
    
    genai.configure(api_key=api_key)
    return True

# === PDF Processing Functions ===
def load_pdf(file_or_buffer):
    """Load a PDF from a file or buffer and return a PdfReader"""
    try:
        return PyPDF2.PdfReader(file_or_buffer)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def download_pdf_from_url(url):
    """Download a PDF from a URL"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading PDF: {e}")
        return None

def split_pdf_pages(reader, start_page, end_page):
    """Split PDF into individual page streams"""
    parts = []
    for i in range(start_page - 1, end_page):
        writer = PyPDF2.PdfWriter()
        writer.add_page(reader.pages[i])
        buffer = io.BytesIO()
        writer.write(buffer)
        buffer.seek(0)
        parts.append(buffer)
    return parts

# === AI Processing Functions ===
def get_model():
    """Get the generative model with the current configuration"""
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 65536,
        "response_mime_type": "text/plain",
    }
    return genai.GenerativeModel(
        model_name=st.session_state.model,
        generation_config=generation_config,
    )

def transcribe_page(page_pdf, model, lang="pl"):
    """Process a PDF page to CSV using the model"""
    file_bytes = page_pdf.getvalue()
    
    # Prompt templates in different languages
    prompts = {
        "pl": "Przetwórz ten dokument na CSV zachowując układ tabeli: Podmiot,Siedziba / miejsce zamieszkania,Lokalizacja przyłączenia,Moc przyłączeniowa [kW],Rodzaj instalacji,Data wydania warunków przyłączenia,Data zawarcia umowy o przyłączenie,Data rozpoczęcia dostarczania energii elektrycznej,Uwagi. Tabelę zwróć w formie ramki CSV.",
        "en": "Process this document into CSV maintaining the table layout: Entity,Headquarters / residence,Connection location,Connection power [kW],Installation type,Date of connection conditions issued,Date of connection agreement,Date of electricity supply commencement,Notes. Return the table as a CSV frame."
    }
    
    prompt = prompts.get(lang, prompts["pl"])
    
    contents = [
        {"mime_type": "application/pdf", "data": file_bytes},
        prompt,
    ]
    response = model.generate_content(contents=contents)
    return response.text

def clean_csv_text(text):
    """Clean the CSV text output from the AI model"""
    return text.replace("```csv", "").replace("```", "").strip()

def parse_csv_to_dataframe(csv_text):
    """Parse CSV text to a DataFrame"""
    csv_io = io.StringIO(csv_text)
    try:
        df = pd.read_csv(
            csv_io,
            sep=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
            on_bad_lines="skip",
            engine='python'
        )
        return df
    except pd.errors.ParserError as e:
        st.warning(f"Warning: Could not parse CSV. Error: {e}")
        return None

def clean_dataframe(df):
    """Clean the DataFrame by removing duplicate headers"""
    if df.empty:
        return df
    
    # Find and remove header rows
    header_indicators = ["Moc przyłączeniowa", "Connection power"]
    mask = df.iloc[:, 3].astype(str).apply(
        lambda x: any(ind in x for ind in header_indicators)
    )
    return df[~mask].reset_index(drop=True)

# === UI Components ===
def render_sidebar():
    """Render the sidebar with settings"""
    with st.sidebar:
        st.markdown('<div class="big-font">⚙️ Settings</div>', unsafe_allow_html=True)
        
        # API Key
        api_key_input = st.text_input(
            "Gemini API Key:",
            value=st.session_state.api_key,
            type="password",
            key="api_key_input"
        )
        
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
        
        col1, col2 = st.columns(2)
        with col1:
            #  Changed this to directly be a link button, styled as a regular button.  Crucially, target="_blank" is needed.
            st.markdown(
                f'<a href="https://aistudio.google.com/app/apikey" target="_blank" style="text-decoration: none;"><button style="border: 1px solid #ccc; border-radius: 4px; padding: 4px 8px; background-color: #fff; color: #333; cursor: pointer;">Get API Key</button></a>',
                unsafe_allow_html=True,
            )
        
        st.divider()
        
        # Model selection
        model = st.selectbox(
            "Model:",
            ["gemini-2.0-flash","gemini-2.0-flash-lite","gemini-2.0-flash-exp", "gemini-2.0-pro-exp", "gemini-2.0-flash-thinking-exp-01-21"],
            index=0,
            key="model_select"
        )
        if model != st.session_state.model:
            st.session_state.model = model
        
        # Language
        language = st.selectbox(
            "Language:",
            ["pl", "en"],
            index=0 if st.session_state.language == "pl" else 1,
            key="language_select"
        )
        if language != st.session_state.language:
            st.session_state.language = language
        
        # Theme
        theme = st.selectbox(
            "Theme:",
            ["light", "dark"],
            index=0 if st.session_state.theme == "light" else 1,
            key="theme_select"
        )
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            apply_theme()
            st.rerun()

def render_header():
    """Render the app header"""
    st.markdown('<div class="big-font">📄 PDF to CSV Conversion</div>', unsafe_allow_html=True)
    
    # Description based on language
    descriptions = {
        "pl": "To narzędzie wykorzystuje AI do konwersji danych tabelarycznych z PDF do CSV.",
        "en": "This tool uses AI to convert tabular data from PDF to CSV."
    }
    st.markdown(descriptions.get(st.session_state.language, descriptions["pl"]))

def render_pdf_upload():
    """Render the PDF upload section"""
    pdf_source = st.radio(
        "Select PDF Source:" if st.session_state.language == "en" else "Wybierz źródło PDF:",
        ("Upload PDF file", "Enter PDF URL") if st.session_state.language == "en" else ("Wgraj plik PDF", "Podaj URL do PDF"),
        horizontal=True
    )

    if pdf_source in ["Upload PDF file", "Wgraj plik PDF"]:
        uploaded_file = st.file_uploader(
            "Upload a PDF file" if st.session_state.language == "en" else "Wgraj plik PDF", 
            type="pdf"
        )
        
        if uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            pdf_reader = load_pdf(uploaded_file)
            if pdf_reader:
                st.session_state.pdf_reader = pdf_reader
                st.session_state.pdf_url = ""
                st.session_state.total_pages = len(pdf_reader.pages)
                st.session_state.end_page = st.session_state.total_pages
                st.rerun()
    else:
        pdf_url_input = st.text_input(
            "Enter PDF URL:" if st.session_state.language == "en" else "Podaj URL do PDF:",
            value=st.session_state.pdf_url
        )
        
        if pdf_url_input and pdf_url_input != st.session_state.pdf_url:
            st.session_state.pdf_url = pdf_url_input
            pdf_buffer = download_pdf_from_url(pdf_url_input)
            
            if pdf_buffer:
                pdf_reader = load_pdf(pdf_buffer)
                if pdf_reader:
                    st.session_state.pdf_reader = pdf_reader
                    st.session_state.uploaded_file = None
                    st.session_state.total_pages = len(pdf_reader.pages)
                    st.session_state.end_page = st.session_state.total_pages
                    st.rerun()

def render_page_selection():
    """Render the page selection section"""
    if not st.session_state.pdf_reader:
        return
    
    total = st.session_state.total_pages
    
    labels = {
        "en": {"total": f"PDF has {total} pages", "start": "Start Page", "end": "End Page"},
        "pl": {"total": f"PDF ma {total} stron", "start": "Strona początkowa", "end": "Strona końcowa"}
    }
    
    lang = st.session_state.language
    
    st.markdown(f"**{labels[lang]['total']}**")
    
    col1, col2 = st.columns(2)
    with col1:
        start_page = st.number_input(
            labels[lang]["start"],
            min_value=1,
            max_value=total,
            value=st.session_state.start_page,
            step=1,
            key="start_page_input"
        )
        st.session_state.start_page = start_page
    
    with col2:
        end_page = st.number_input(
            labels[lang]["end"],
            min_value=1,
            max_value=total,
            value=st.session_state.end_page,
            step=1,
            key="end_page_input"
        )
        st.session_state.end_page = end_page

def render_buttons():
    """Render action buttons"""
    if not st.session_state.pdf_reader:
        return
    
    labels = {
        "en": {"convert": "Convert", "stop": "STOP", "reset": "Reset"},
        "pl": {"convert": "Konwertuj", "stop": "STOP", "reset": "Od nowa"}
    }
    
    lang = st.session_state.language
    
    if st.session_state.start_page > st.session_state.end_page:
        st.error(
            "Start page cannot be greater than end page" if lang == "en" else 
            "Strona początkowa nie może być większa niż końcowa"
        )
        return
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button(labels[lang]["convert"], type="primary", disabled=st.session_state.conversion_running):
            if not configure_api():
                st.error(
                    "API key is required" if lang == "en" else
                    "Klucz API jest wymagany"
                )
                return
            
            st.session_state.conversion_running = True
            st.session_state.stop_button_pressed = False
            st.session_state.processed_pages = 0
            # Clear previous results
            st.session_state.df_results = pd.DataFrame(
                columns=st.session_state.df_results.columns
            )
            st.rerun()
    
    with col2:
        if st.button(labels[lang]["stop"], disabled=not st.session_state.conversion_running):
            st.session_state.stop_button_pressed = True
    
    with col3:
        if st.button(labels[lang]["reset"]):
            for key in ["df_results", "pdf_reader", "uploaded_file", "pdf_url", 
                       "start_page", "end_page", "total_pages", "conversion_running", 
                       "stop_button_pressed", "processed_pages"]:
                if key == "df_results":
                    st.session_state.df_results = pd.DataFrame(
                        columns=st.session_state.df_results.columns
                    )
                else:
                    st.session_state[key] = init_session_state.__defaults__[0].get(key)
            st.rerun()

def run_conversion():
    """Run the PDF to CSV conversion process"""
    if not st.session_state.conversion_running:
        return
    
    # Get model
    model = get_model()
    
    # Get PDF pages
    parts = split_pdf_pages(
        st.session_state.pdf_reader, 
        st.session_state.start_page, 
        st.session_state.end_page
    )
    
    # Set up metrics placeholders
    status_container = st.empty()
    with status_container.container():
        st.info(
            "Processing pages..." if st.session_state.language == "en" else
            "Przetwarzanie stron..."
        )
    
    metrics_container = st.empty()
    table_container = st.empty()
    
    # Processing logic
    start_time = time.time()
    
    for i, part in stqdm(enumerate(parts), total=len(parts)):
        if st.session_state.stop_button_pressed:
            with status_container.container():
                st.warning(
                    "Conversion stopped by user" if st.session_state.language == "en" else
                    "Konwersja zatrzymana przez użytkownika"
                )
            break
        
        page_start_time = time.time()
        
        # Process page
        csv_text = transcribe_page(part, model, st.session_state.language)
        csv_text = clean_csv_text(csv_text)
        
        # Parse to DataFrame
        df_page = parse_csv_to_dataframe(csv_text)
        
        if df_page is not None and not df_page.empty:
            # Append to results
            st.session_state.df_results = pd.concat(
                [st.session_state.df_results, df_page], 
                ignore_index=True
            )
            
            # Clean results
            st.session_state.df_results = clean_dataframe(st.session_state.df_results)
            
            # Update processed pages counter
            st.session_state.processed_pages += 1
        
        # Update metrics
        page_time = time.time() - page_start_time
        total_time = time.time() - start_time
        pages_remaining = len(parts) - (i + 1)
        
        with metrics_container.container():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Time Elapsed" if st.session_state.language == "en" else "Czas przetwarzania",
                    str(timedelta(seconds=int(total_time)))
                )
            with col2:
                est_remaining = page_time * pages_remaining if pages_remaining > 0 else 0
                st.metric(
                    "Estimated Time Remaining" if st.session_state.language == "en" else "Szacowany czas do ukończenia",
                    str(timedelta(seconds=int(est_remaining)))
                )
            with col3:
                st.metric(
                    "Speed per Page" if st.session_state.language == "en" else "Prędkość na stronę",
                    f"{page_time:.2f}s"
                )
        
        # Update table
        with table_container.container():
            st.dataframe(
                st.session_state.df_results,
                use_container_width=True,
                hide_index=True
            )
        
        # Rate limiting
        if i < len(parts) - 1 and not st.session_state.stop_button_pressed:
            time.sleep(6)  # 6 seconds between requests (10 RPM)
    
    # Processing complete or stopped
    if not st.session_state.stop_button_pressed and st.session_state.processed_pages > 0:
        with status_container.container():
            st.success(
                "Conversion complete" if st.session_state.language == "en" else
                "Konwersja zakończona"
            )
    
    # Reset conversion running flag
    st.session_state.conversion_running = False

def render_download_button():
    """Render the download button for results"""
    if st.session_state.df_results.empty:
        return
    
    csv_string = st.session_state.df_results.to_csv(index=False)
    
    st.download_button(
        "Download CSV" if st.session_state.language == "en" else "Pobierz CSV",
        csv_string,
        file_name="result.csv",
        mime="text/csv",
        type="primary"
    )

def main():
    """Main function to run the app"""
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    
    # PDF Upload section
    with st.expander(
        "PDF Upload" if st.session_state.language == "en" else "Wgrywanie PDF", 
        expanded=True
    ):
        render_pdf_upload()
        render_page_selection()
        render_buttons()
    
    # Run conversion if active
    if st.session_state.conversion_running:
        run_conversion()
    
    # Results section
    if not st.session_state.df_results.empty:
        st.markdown(
            "### Results" if st.session_state.language == "en" else "### Wyniki"
        )
        st.dataframe(
            st.session_state.df_results,
            use_container_width=True,
            hide_index=True
        )
        render_download_button()
    # Add footer
    st.markdown("---")
    st.markdown("Stworzone przez Przemysław Suchowiejko - AethernaTolith (2025)")
if __name__ == "__main__":
    main()
