# 📚 Personalized Study Schedule Planner with Adaptive Quiz Generator

A web-based application that helps students manage their study schedules efficiently and practice through automatically generated quizzes based on uploaded PDFs. The planner dynamically adjusts to individual performance, retention rates, and upcoming exams while offering real-time feedback and progress tracking.

---

## 🚀 Features

✅ **Personalized Study Planner**  
- Prioritizes topics based on performance, retention, and exam dates.  
- Forecasts memory retention using spaced repetition.  
- Suggests daily schedules tailored to student needs.

✅ **Progress Tracking**  
- Visual graphs to track performance and retention.  
- Actionable recommendations for improvement.  
- Marks completed topics and tracks study trends.

✅ **Adaptive Quiz Generator**  
- Extracts text from uploaded PDFs to create quizzes.  
- Detects Q&A format or generates new questions from text.  
- Provides instant feedback and shows correct answers.  

✅ **User-Friendly Interface**  
- Interactive design with pastel colors.  
- Charts and progress bars to motivate users.  
- Easy navigation between planner, tracker, and quiz.

---

## 🧠 Problem Statement

Students often find it hard to plan study schedules effectively, leading to forgotten topics and last-minute cramming. Each learner has different strengths, weaknesses, and deadlines, making generic schedules inefficient. This project solves these problems by offering personalized planning, tracking, and practice tools that adapt to student needs.

---

## 🎯 Project Outcome

The application provides students with a structured study plan, forecasts memory retention, and suggests topics needing revision. Users can upload PDFs to generate quizzes that test their knowledge. The planner helps students stay organized, track performance, and boost confidence with real-time feedback.

---

## 🎯 Objectives

- Provide customized schedules based on user input.  
- Improve retention through spaced repetition forecasting.  
- Generate quizzes from educational material automatically.  
- Visualize progress and performance trends.  
- Engage students by providing actionable insights.

---

## ⚙️ Methodology

**Approach:**  
Collects user data (courses, topics, exam dates, performance), forecasts retention using mathematical models, and prioritizes topics needing focus.

**Dataset:**  
User-provided course information and educational PDFs containing notes or textbooks.

**Technologies:**  
- Python  
- Streamlit  
- Plotly  
- pdfplumber  
- Regex  
- datetime module

---

## 🛠 Implementation

1. Designed input forms for courses, topics, and performance.
2. Developed algorithms for forecasting retention rates.
3. Created prioritization based on urgency and performance.
4. Built adaptive quizzes using text extraction from PDFs.
5. Integrated charts and progress bars for visualization.
6. Handled errors for unreadable PDFs and insufficient data.

---

## 📂 Project Structure
'''
personalized_study_planner/
├── study_planner.py
├── requirements.txt
├── README.md
'''

---

## 📦 Installation

1. Clone the repository:  
   `git clone https://github.com/Alreyaa/personalized_study_planner.git`

2. Create and activate a virtual environment:  
   `python -m venv venv`  
   `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows)

3. Install dependencies:  
   `pip install -r requirements.txt`

4. Run the app:  
   `streamlit run study_planner.py`

---

## 📖 Usage

1. Input courses, exam dates, and performance.
2. View schedules prioritized by retention and urgency.
3. Track progress with charts.
4. Upload PDFs to generate quizzes and test knowledge.

---

## 📈 Results & Observations

- Efficient planning based on real-time data.
- Better retention through scheduled reviews.
- Engaging quizzes that target weak areas.
- Motivating progress tracking through graphs.

---

## ✅ Conclusion & Future Work

**Conclusion:**  
The project helps students plan and review efficiently, improving academic performance through personalized guidance and adaptive quizzes.

**Future Work:**  
- Add AI-powered difficulty adjustment.
- Support image-based PDFs.
- Create mobile apps for accessibility.
- Sync with calendars and learning platforms.
