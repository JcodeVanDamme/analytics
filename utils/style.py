import streamlit as st

primaryColor = "#66C0F4"
backgroundColor = "#2A475E"
secondaryBackgroundColor = "#171A21"
altColor = "rgba(200,200,200,1.0)"
textColor = "#ffffff"

def apply_global():
    st.markdown(f"""
            <style>
            /* 1. MAIN HEADERS */
            h1 {{
                font-weight: 700 !important;
                letter-spacing: 0.08em !important;
                text-transform: uppercase !important;
            }}
            h2 {{
                font-weight: 700 !important;
                letter-spacing: 0.08em !important;
            }}
            
            .centered-header, .centered-header h1, .centered-header h3 {{
                text-align: center !important;
                width: 100% !important;
                display: block !important; /* Forces the div block to stretch across the full row */
            }}
            
            /* 2. THE EXPANDER TITLE ONLY */
            [data-testid="stSidebar"] [data-testid="stExpanderSummary"] p {{
                font-weight: 800 !important;
                text-transform: uppercase !important;
                font-size: 30;
            }}
            
            /* 3. TARGET THE REST OF THE P TAGS INSIDE THE EXPANDER BODY */
            [data-testid="stSidebar"] [data-testid="stExpanderDetails"] p {{
                font-weight: 300 !important;
                letter-spacing: 0.02em !important;
            }}
            
            /* ✨ NEW: TARGET TEXT RUNNING EXCLUSIVELY THROUGH YOUR WRITE() FUNCTION */
            .custom-write-text {{
                font-weight: 300!important;
                letter-spacing: -0.02em !important;
            }}
        
            /* Target the metric descriptor label */
            [data-testid="stMetricLabel"] > div {{
                text-transform: uppercase !important;
                letter-spacing:  0.08em !important;
            }}
            
            /* Styles the main body cells */
            div[data-testid="stTable"] table tbody td {{
                background-color: {secondaryBackgroundColor} !important;
            }}
            
            /* Styles the row index cells (your Ranks) */
            div[data-testid="stTable"] table tbody th {{
                background-color: {secondaryBackgroundColor} !important;
            }}
    
            /* Styles the top header row */
            div[data-testid="stTable"] table thead tr th {{
                background-color: {secondaryBackgroundColor} !important;

            }}
            /* Changes the background color and text color inside the tooltip box */
            div[data-testid="stTooltipContent"] {{
                background-color: {backgroundColor} !important;
                border: 2px solid {textColor} !important; /* Adjust your hex color and width here */
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5);
                border-radius: 6px !important;
            }}
    """, unsafe_allow_html=True)

def heading(text, center=False):
    if center:
        # Wrap the markdown in a styled div container block
        st.markdown(f'<div class="centered-header"><h1>{str(text)}</h1></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"# {str(text)}")


def subheading(text, center=False, upper=False):
    if center:
        st.markdown(f'<div class="centered-header"><h3>{str(text)}</h3></div>', unsafe_allow_html=True)
    elif upper:
        st.markdown(f"### {str(text.upper())}")
    else:
        st.markdown(f"### {str(text)}")


def suss_heading(text):
    st.markdown(f'<div style="color: {altColor};"><h5>{str(text)}</h5></div>', unsafe_allow_html=True)


def write(text, center=False):
    if center:
        st.markdown(
            f'<span class="centered-header custom-write-text">{str(text)}</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<span class="custom-write-text">{str(text)}</span>',
            unsafe_allow_html=True
        )

def style_containers(count):
    css = ""
    for i in range(count):
        css += f"""
        .st-key-game_card_{i} {{
            background-color: {secondaryBackgroundColor};
        }}
        """

    st.html(f"<style>{css}</style>")