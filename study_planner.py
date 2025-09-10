import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import plotly.express as px
import pdfplumber 
import random
import io
import re

# Q&A Handling

def is_qa_format(text):
    """Detect if the text contains Q&A patterns like 'Question:' and 'Answer:'"""
    return bool(re.search(r"Question\s*[:\-]", text, re.IGNORECASE)) and bool(re.search(r"Answer\s*[:\-]", text, re.IGNORECASE))

def convert_qa_to_quiz(text, num_questions=5):
    """Convert Q&A formatted text into quiz questions"""
    questions = []
    pattern = r"(Question\s*[:\-].*?)(Answer\s*[:\-].*?)(?=(Question\s*[:\-]|$))"
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    
    all_answers = []
    for q_text, a_text, _ in matches:
        question = re.sub(r"Question\s*[:\-]", "", q_text, flags=re.IGNORECASE).strip()
        answer = re.sub(r"Answer\s*[:\-]", "", a_text, flags=re.IGNORECASE).strip()
        all_answers.append(answer)
    
    if not matches or len(all_answers) == 0:
        return []
    
    random.shuffle(matches)
    for q_text, a_text, _ in matches[:num_questions]:
        question = re.sub(r"Question\s*[:\-]", "", q_text, flags=re.IGNORECASE).strip()
        answer = re.sub(r"Answer\s*[:\-]", "", a_text, flags=re.IGNORECASE).strip()

        # Create distractors from other answers or generic ones
        distractors = [ans for ans in all_answers if ans != answer]
        random.shuffle(distractors)
        selected_distractors = distractors[:3]
        
        if len(selected_distractors) < 3:
            generic_distractors = ["cell", "tissue", "organ", "system", "enzyme", "hormone", "protein", "nucleus", "membrane"]
            while len(selected_distractors) < 3:
                distractor = random.choice(generic_distractors)
                if distractor.lower() not in [d.lower() for d in selected_distractors] and distractor.lower() != answer.lower():
                    selected_distractors.append(distractor)
        
        options = selected_distractors[:3] + [answer]
        random.shuffle(options)

        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })
    
    return questions

# Retention Function

def adjusted_retention(retention_rate, last_studied, half_life=7, forecast_days=14):
    last_studied = datetime.strptime(last_studied, "%Y-%m-%d")
    retention_forecast = []
    for day in range(forecast_days):
        days_since = (datetime.now() - last_studied).days + day
        adj_ret = retention_rate * math.exp(-days_since / half_life)
        retention_forecast.append(adj_ret)
    return retention_forecast

#Topic Functions

def prioritize_topics(courses, days_until_exam_threshold):
    topic_list = []
    for course in courses:
        exam_date = datetime.strptime(course['exam_date'], "%Y-%m-%d")
        days_until_exam = (exam_date - datetime.now()).days
        for topic in course['topics']:
            adj_ret = adjusted_retention(topic['retention_rate'], topic['last_studied'])[0]
            urgency = max(0, days_until_exam_threshold - days_until_exam)
            priority_score = (1 - adj_ret) + (1 - topic['performance']/100) + urgency*0.1
            topic_list.append({
                "course": course['course_name'],
                "topic": topic['topic'],
                "performance": topic['performance'],
                "adj_retention": adj_ret,
                "days_until_exam": days_until_exam,
                "priority_score": priority_score,
                "completed": topic.get("completed", False)
            })
    topic_list.sort(key=lambda x: x['priority_score'], reverse=True)
    return topic_list

#Generate schedule Functions
def generate_schedule(topic_list, daily_hours, max_hours_per_topic=2):
    days_until_exams = [t['days_until_exam'] for t in topic_list if not t['completed']]
    if not days_until_exams:
        return []
    max_days = max(1, min(days_until_exams))
    
    schedule = []
    for day in range(max_days):
        day_schedule = []
        hours_remaining = daily_hours
        for topic in topic_list:
            if topic['completed']:
                continue
            if hours_remaining <= 0:
                break
            allocated_hours = min(max_hours_per_topic, hours_remaining)
            day_schedule.append({
                "course": topic['course'],
                "topic": topic['topic'],
                "hours": allocated_hours
            })
            hours_remaining -= allocated_hours
        schedule.append({
            "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
            "topics": day_schedule
        })
    return schedule

#Generate reccomendations Functions
def generate_recommendations(topic_list):
    recommendations = []
    for topic in topic_list:
        if topic['completed']:
            continue
        if topic['adj_retention'] < 0.5:
            recommendations.append(f"Revise {topic['topic']} ({topic['course']}) frequently.")
        if topic['performance'] < 50:
            recommendations.append(f"Focus on {topic['topic']} ({topic['course']}) to improve performance.")
    return recommendations

#Generate Quiz

def generate_quiz_from_text(text, num_questions=5):
    if is_qa_format(text):
        return convert_qa_to_quiz(text, num_questions)

    questions = []
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
    
    if len(sentences) < 5:
        return []
    
    random.shuffle(sentences)
    
    common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
                    'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'will', 'would', 
                    'could', 'should', 'this', 'that', 'these', 'those', 'a', 'an', 'question', 'answer'}

    for i, sentence in enumerate(sentences):
        if len(questions) >= num_questions:
            break
        sentence = sentence.strip()
        if not sentence or len(sentence) < 20:
            continue
        if re.search(r'question\s*[:\-]|answer\s*[:\-]', sentence, re.IGNORECASE):
            continue
        words = [w.strip() for w in sentence.split() if 3 <= len(w.strip()) <= 15]
        if len(words) < 5:
            continue
        suitable_words = [w for w in words if w.lower() not in common_words and len(w) > 3]
        if not suitable_words:
            continue
        answer = random.choice(suitable_words)
        question_text = sentence.replace(answer, "_____", 1)

        distractors = []
        for other_sentence in sentences[:20]:
            if other_sentence == sentence:
                continue
            other_words = [w.strip() for w in other_sentence.split() if 3 <= len(w.strip()) <= 15]
            suitable_distractors = [w for w in other_words if w.lower() not in common_words and w != answer and len(w) > 2]
            distractors.extend(suitable_distractors)

        distractors = list(set(distractors))
        random.shuffle(distractors)
        selected_distractors = distractors[:3]

        if len(selected_distractors) < 3:
            generic_distractors = ["concept", "process", "system", "method", "approach", "technique", "principle", "theory", "model", "framework"]
            while len(selected_distractors) < 3:
                distractor = random.choice(generic_distractors)
                if distractor != answer and distractor not in selected_distractors:
                    selected_distractors.append(distractor)

        options = selected_distractors[:3] + [answer]
        random.shuffle(options)

        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer
        })

    return questions

# Streamlit UI

st.set_page_config(page_title="📚 Study Planner", layout="wide")
st.title("📚 Personalized Study Schedule Planner")

page = st.sidebar.selectbox("Navigate", ["Input Courses", "Schedule", "Progress Tracker", "Adaptive Quiz"])

if 'courses' not in st.session_state:
    st.session_state.courses = []

# Input Courses

if page == "Input Courses":
    st.header("📝 Enter your courses and topics")
    daily_hours = st.number_input("Daily available study hours:", 1, 12, 4)
    days_until_exam_threshold = st.number_input("Days threshold for upcoming exams:", 1, 30, 10)
    
    courses = []
    num_courses = st.number_input("Number of courses:", 1, 10, 2)
    
    for i in range(num_courses):
        st.markdown(f"### Course {i+1}")
        course_name = st.text_input(f"Course name {i+1}", key=f"course_name_{i}")
        exam_date = st.date_input(f"Exam date for {course_name}", key=f"exam_date_{i}")
        num_topics = st.number_input(f"Number of topics in {course_name}", 1, 20, key=f"num_topics_{i}")
        topics = []
        for j in range(num_topics):
            st.markdown(f"**Topic {j+1}**")
            topic_name = st.text_input(f"Topic name {j+1} in {course_name}", key=f"topic_name_{i}_{j}")
            performance = st.number_input(f"Performance (%) in {topic_name}", 0, 100, key=f"performance_{i}_{j}")
            last_studied = st.date_input(f"Last studied date for {topic_name}", key=f"last_studied_{i}_{j}")
            retention_rate = st.slider(f"Retention rate for {topic_name}", 0.0, 1.0, 0.5, key=f"retention_{i}_{j}")
            completed = st.checkbox("Completed?", key=f"completed_{i}_{j}")
            topics.append({
                "topic": topic_name,
                "performance": performance,
                "last_studied": last_studied.strftime("%Y-%m-%d"),
                "retention_rate": retention_rate,
                "completed": completed
            })
        courses.append({
            "course_name": course_name,
            "exam_date": exam_date.strftime("%Y-%m-%d"),
            "topics": topics
        })
    
    if st.button("Save Courses"):
        st.session_state.courses = courses
        st.session_state.daily_hours = daily_hours
        st.session_state.days_until_exam_threshold = days_until_exam_threshold
        st.success("Courses saved successfully!")

# Schedule

elif page == "Schedule":
    st.header("📅 Daily Study Schedule")
    topic_list = prioritize_topics(st.session_state.courses, st.session_state.days_until_exam_threshold if 'days_until_exam_threshold' in st.session_state else 10)
    schedule = generate_schedule(topic_list, st.session_state.daily_hours if 'daily_hours' in st.session_state else 4)
    
    if not schedule:
        st.info("✅ All topics completed or exams over!")
    else:
        for day in schedule:
            with st.expander(f"📌 {day['date']}"):
                for t in day['topics']:
                    color = "#171717"
                    if t['hours'] >= 2:
                        color = "#171717"
                    st.markdown(
                        f"<div style='background-color:{color};padding:8px;border-radius:8px;margin-bottom:5px;'>"
                        f"<b>{t['course']}</b>: {t['topic']} — {t['hours']} hrs</div>",
                        unsafe_allow_html=True
                    )
        recommendations = generate_recommendations(topic_list)
        st.markdown("### 💡 Recommendations")
        for rec in recommendations:
            st.write(f"- {rec}")

# Progress Tracker

elif page == "Progress Tracker":
    st.header("📊 Topic Retention & Performance")
    for course_idx, course in enumerate(st.session_state.courses):
        st.subheader(course['course_name'])
        cols = st.columns(2)
        for topic_idx, topic in enumerate(course['topics']):
            with cols[topic_idx % 2]:
                retention_forecast = adjusted_retention(
                    topic['retention_rate'], 
                    topic['last_studied'], 
                    forecast_days=14
                )
                df = pd.DataFrame({
                    "Day": [i+1 for i in range(len(retention_forecast))],
                    "Retention": retention_forecast
                })
                fig = px.line(
                    df, 
                    x="Day", 
                    y="Retention", 
                    title=f"{topic['topic']} Retention Forecast",
                    range_y=[0,1], 
                    line_shape="spline", 
                    template="plotly_white",
                    color_discrete_sequence=["#FFB6C1"]
                )
                st.plotly_chart(fig, use_container_width=True, key=f"{course_idx}_{topic_idx}_chart")
                
                st.progress(int(topic['performance']))
                st.markdown(
                    f"**Performance:** {topic['performance']}% | "
                    f"**Current Retention:** {retention_forecast[0]:.2f}"
                )
                if topic['completed']:
                    st.success("✅ Completed")
                else:
                    st.info("🔄 Not Completed")

# Adaptive Quiz

elif page == "Adaptive Quiz":
    st.header("📝 Adaptive Quiz Generator")

    if 'quiz_index' not in st.session_state:
        st.session_state.quiz_index = 0
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
    if 'quiz_uploaded' not in st.session_state:
        st.session_state.quiz_uploaded = False
    if 'uploaded_file_bytes' not in st.session_state:
        st.session_state.uploaded_file_bytes = None

    uploaded_file = st.file_uploader("Upload a PDF to generate quiz questions", type=["pdf"])

    if uploaded_file and st.session_state.uploaded_file_bytes is None:
        st.session_state.uploaded_file_bytes = uploaded_file.read()

    if st.session_state.uploaded_file_bytes and not st.session_state.quiz_uploaded:
        if st.button("Generate Quiz Questions"):
            with st.spinner("Extracting text from PDF..."):
                try:
                    with pdfplumber.open(io.BytesIO(st.session_state.uploaded_file_bytes)) as pdf:
                        text = ""
                        page_count = 0
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + " "
                                page_count += 1
                    
                    if len(text.strip()) < 50:
                        st.error("⚠ Very little text found in the PDF. Please try a different file.")
                        st.info("**Debug info:** The PDF might be image-based or have very little readable text.")
                    else:
                        with st.spinner("Generating quiz questions..."):
                            questions = generate_quiz_from_text(text, 5)
                            
                            if questions:
                                st.session_state.quiz_questions = questions
                                st.session_state.quiz_index = 0
                                st.session_state.quiz_score = 0
                                st.session_state.quiz_uploaded = True
                                st.success(f"✅ Generated {len(questions)} quiz questions!")
                                st.rerun()
                            else:
                                st.error("⚠ Could not generate questions from this PDF.")
                                st.info("""
                                **Possible reasons:**
                                - PDF contains mostly images or scanned text
                                - Text is too fragmented or poorly formatted
                                - Content doesn't have enough meaningful sentences
                                
                                **Try:**
                                - A different PDF with more text content
                                - Educational materials like textbooks or articles
                                - PDFs with clear, readable text formatting
                                """)
                except Exception as e:
                    st.error(f"⚠ Error processing PDF: {str(e)}")
                    st.info("Try uploading a different PDF file.")

    if st.session_state.quiz_questions:
        q_idx = st.session_state.quiz_index
        if q_idx < len(st.session_state.quiz_questions):
            q = st.session_state.quiz_questions[q_idx]
            st.markdown(f"### Question {q_idx + 1} of {len(st.session_state.quiz_questions)}")
            st.markdown(f"**{q['question']}**")
            
            with st.form(f"quiz_form_{q_idx}"):
                answer = st.radio("Choose an answer:", q['options'])
                submitted = st.form_submit_button("Submit Answer")
                
                if submitted:
                    if answer == q['answer']:
                        st.success("✅ Correct!")
                        st.session_state.quiz_score += 1
                    else:
                        st.error(f"❌ Incorrect! The correct answer was: **{q['answer']}**")
                    st.session_state.quiz_index += 1
                    st.rerun()

            st.progress((q_idx + 1) / len(st.session_state.quiz_questions))
            st.markdown(f"**Current Score:** {st.session_state.quiz_score}/{q_idx + 1}")
        else:
            final_score = st.session_state.quiz_score
            total_questions = len(st.session_state.quiz_questions)
            percentage = (final_score / total_questions) * 100
            
            st.success(f"🎉 Quiz Completed!")
            st.markdown(f"### Final Score: {final_score}/{total_questions} ({percentage:.1f}%)")
            
            if percentage >= 80:
                st.balloons()
                st.markdown("🌟 **Excellent work!** You have a strong understanding of the material.")
            elif percentage >= 60:
                st.markdown("👍 **Good job!** Consider reviewing the topics you missed.")
            else:
                st.markdown("📚 **Keep studying!** Review the material and try again.")
            
            if st.button("Start New Quiz"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_index = 0
                st.session_state.quiz_score = 0
                st.session_state.quiz_uploaded = False
                st.session_state.uploaded_file_bytes = None
                st.rerun()
    else:
        if uploaded_file and not st.session_state.quiz_uploaded:
            st.info("Click 'Generate Quiz Questions' after uploading the PDF.")
