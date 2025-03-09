import os
from datetime import datetime, date
from dotenv import load_dotenv
import pytz
import streamlit as st
from services.google_calendar import get_meetings
from services.ai_services import generate_summary, text_to_speech


def initialize_environment():
    """Load and validate environment configuration"""
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env')
                )  # Fixed missing parenthesis

    required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        st.error(f"Missing environment variables: {', '.join(missing)}")
        st.stop()

    timezone = os.getenv("TIMEZONE", "Asia/Kolkata")
    try:
        pytz.timezone(timezone)
    except pytz.UnknownTimeZoneError:
        st.error("Invalid TIMEZONE in .env, defaulting to Asia/Kolkata")
        timezone = "Asia/Kolkata"

    return timezone


TIMEZONE = initialize_environment()

st.set_page_config(
    page_title="AI Digital Twin",
    layout="wide",
    page_icon="🤖",
)


def initialize_session_state():
    """Initialize or reset session state"""
    session_defaults = {
        'summary': None,
        'audio': None,
        'meetings': [],
        'selected_meeting': None
    }
    for key, val in session_defaults.items():
        st.session_state.setdefault(key, val)


initialize_session_state()


def format_datetime(dt) -> str:
    """Handle both datetime and date objects"""
    if isinstance(dt, datetime):
        return dt.astimezone(pytz.timezone(TIMEZONE)).strftime('%d %b %Y %I:%M %p')
    elif isinstance(dt, date):
        return dt.strftime('%d %b %Y')
    return "Invalid date"


def main():
    st.title("🤖 AI Meeting Assistant")

    with st.sidebar:
        st.header("Settings")
        if st.button("🔄 Refresh Meetings"):
            try:
                st.session_state.meetings = get_meetings()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to refresh meetings: {str(e)}")

    try:
        if not st.session_state.meetings:
            st.session_state.meetings = get_meetings()
    except Exception as e:
        st.error(f"❌ Error fetching meetings: {str(e)}")
        return

    st.subheader("📅 Upcoming Meetings")
    if not st.session_state.meetings:
        st.info("No upcoming meetings found")
        return

    for idx, meeting in enumerate(st.session_state.meetings):
        try:
            col1, col2 = st.columns([4, 1])

            with col1:
                meeting_title = meeting.get('summary', 'Untitled Meeting')
                start_data = meeting.get('start', {})
                end_data = meeting.get('end', {})

                start_time = start_data.get(
                    'datetime') or start_data.get('date')
                end_time = end_data.get('datetime') or end_data.get('date')

                with st.expander(f"{meeting_title} - {format_datetime(start_time)}"):
                    time_str = f"{format_datetime(start_time)} - {format_datetime(end_time)}"
                    attendees = meeting.get('attendees', [])
                    description = meeting.get('description', 'No description')

                    st.write(f"**Time:** {time_str}")
                    st.write(
                        f"**Attendees:** {', '.join(attendees) if attendees else 'None'}")
                    st.write(f"**Description:** {description}")

            with col2:
                if st.button("Generate AI Summary", key=f"btn_{idx}"):
                    st.session_state.selected_meeting = idx
                    with st.spinner("Generating summary..."):
                        try:
                            desc = meeting.get('description', '')
                            st.session_state.summary = generate_summary(desc)
                            if st.session_state.summary:
                                st.session_state.audio = text_to_speech(
                                    st.session_state.summary)
                        except Exception as e:
                            st.error(f"AI processing failed: {str(e)}")
        except KeyError as e:
            st.error(
                f"Error displaying meeting: Missing {str(e)} in event data")
            continue

    if st.session_state.summary and st.session_state.selected_meeting is not None:
        st.divider()
        st.subheader("📝 AI Generated Summary")
        st.markdown(st.session_state.summary)

        if st.session_state.audio:
            st.audio(st.session_state.audio, format='audio/mp3')
            if st.button("Clear Summary"):
                initialize_session_state()
                st.rerun()


if __name__ == "__main__":
    main()
