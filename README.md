## 🗓️ Meeting Scheduler Bot

An AI-powered meeting scheduler that allows users to schedule meetings based on natural language input. 

## ✨ Features

- **Natural Language Understanding**: Parses meeting requests in natural language.
- **Timezone Detection**: Automatically determines time zones based on user location.
- **User-Friendly Interface**: Simple input fields for meeting requests and location.
- **Participant Extraction**: Identifies participants from the request text.

## 🛠️ Technologies Used

- **Python**: Core programming language.
- **Streamlit**: Framework for building the web app.
- **Transformers**: Hugging Face library for Natural Language Processing.
- **Geopy**: For geolocation services.
- **Dateparser**: For flexible date parsing.
- **Timezonefinder**: To find time zones based on coordinates.

## 📦 Installation

To get started with the project, clone the repository and install the required packages:

```bash
git clone https://github.com/Ikuku-Success/meeting_scheduler.git
cd meeting_scheduler
pip install -r requirements.txt
```

## 🚀 How to Run

1. Ensure you have all the dependencies installed.
2. Start the Streamlit application:

```bash
streamlit run app.py
```

3. Open your browser and navigate to `http://localhost:8501` to access the app.

## 📊 Usage

1. Enter your meeting request in the text area.
2. Fill in your country, state, and city in the input fields.
3. Click the "Schedule Meeting" button.
4. The bot will provide a confirmation of the scheduled meeting details.


## 🌟 Acknowledgements

- Thanks to [Hugging Face](https://huggingface.co/) for their Transformers library.
- Special thanks to [Streamlit](https://streamlit.io/) for making web app development easy and intuitive.
```
