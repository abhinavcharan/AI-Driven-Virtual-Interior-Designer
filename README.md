# AI-Driven-Virtual-Interior-Designer

A Streamlit-based web application that helps users visualize different interior design styles by processing room photos and providing personalized recommendations.

## Features

- **Style Visualization**: Transform room photos with 6 different design styles (Modern, Traditional, Industrial, Scandinavian, Bohemian, Minimalist)
- **Smart Recommendations**: Get furniture and color palette suggestions based on selected style
- **Design History**: Save and manage multiple design iterations
- **Interactive Interface**: User-friendly interface with earthy, aesthetic design
- **Budget Planning**: Set budget ranges and get appropriate recommendations

## Demo

![Demo Screenshot](assets/demo-screenshot.png)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-interior-design-assistant.git
cd ai-interior-design-assistant
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

5. Open your browser and navigate to `http://localhost:8501`

## Deployment

### Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Click "New app" and connect your GitHub repository
4. Select the repository and set the main file path to `app.py`
5. Deploy!

### Docker Deployment

Build and run using Docker:

```bash
docker build -t interior-design-app .
docker run -p 8501:8501 interior-design-app
```

### Heroku Deployment

1. Install Heroku CLI
2. Create a new Heroku app:
```bash
heroku create your-app-name
```

3. Deploy:
```bash
git push heroku main
```
