# 🛡️ RoadGuard AI

AI Road Guard is an AI-powered road safety system that detects traffic violations, road hazards, and vehicles in real time using computer vision and deep learning. The application provides instant alerts, improves traffic monitoring, and enhances road safety through intelligent video analysis.

## ✨ Features

- **Real-time detection** of traffic violations, road hazards, and vehicles using computer vision
- **Instant alerts** to flag safety issues as they happen
- **Traffic monitoring** dashboard for continuous oversight
- **Deep learning models** trained for road safety analysis
- Interactive **Streamlit** web interface

## 🗂️ Project Structure

```
RoadGuard-AI/
├── .streamlit/       # Streamlit app configuration
├── ai/               # AI/ML models and inference logic
├── assets/           # Images, icons, and static assets
├── components/        # Reusable UI components
├── database/         # Database models and connection logic
├── pages/            # Streamlit multi-page app views
├── training/         # Model training scripts and notebooks
├── utils/            # Helper/utility functions
├── app.py            # Main application entry point
├── packages.txt       # System-level package dependencies
└── requirements.txt   # Python package dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/Hammad7-dot/RoadGuard-AI-.git
   cd RoadGuard-AI-
   ```

2. Create a virtual environment (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application
   ```bash
   streamlit run app.py
   ```

The app should now be running locally — Streamlit will open it in your browser automatically (typically at `http://localhost:8501`).

## 🧠 Tech Stack

- **Python** — core language and AI/ML logic
- **Streamlit** — web app framework and UI
- **Computer Vision / Deep Learning** — for detection and classification (see `ai/` and `training/`)
- **CSS** — custom styling

## 📊 Model Training

Training scripts and resources for the detection models are located in the `training/` directory. Refer to the scripts there for dataset preparation, training configuration, and evaluation steps.

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

No license specified yet. Consider adding one (e.g., MIT, Apache 2.0) to clarify usage rights.

## 👤 Author

**Muhammad Hammad** ([@Hammad7-dot](https://github.com/Hammad7-dot))
