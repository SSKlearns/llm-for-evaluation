import streamlit as st
import pandas as pd
from conf import Secret
from openai import OpenAI

SECRETS = Secret()
client = OpenAI(api_key=SECRETS["OPENAI_API_KEY"])
TEMPERATURE = 0.3

def convert_df_to_csv(df):
    csv = df.to_csv(index=False)
    return csv

# Initialize session state
if 'csv_data' not in st.session_state:
    st.session_state.csv_data = None
   
# Streamlit interface
st.title("Exam Scoring System")

# File uploaders
questions = st.text_area("Enter the question")
sample_answer = st.text_area("Enter a sample answer")
instructions = st.text_area("Enter evaluation instructions")
max_marks = st.number_input("Enter Maximum Marks", min_value=0)
student_answers = st.file_uploader("Upload Students Answers", type=['csv', 'xlsx'], on_change=lambda: setattr(st.session_state, 'csv_data', None))

if st.button("Calculate Scores", type="primary"):
    if questions and sample_answer and student_answers and max_marks and instructions:
        # Read the files
        # Assuming the files are in a simple CSV format
        try:
            answers_df = pd.read_csv(student_answers)
            if (list(answers_df.keys()) != ["Name", "Answer"]):
                st.error("Please make sure first row of the CSV is of format \"Name,Answer\"")
                # Exit the program
                exit()
                
            names = list(answers_df["Name"])
            answers = list(answers_df["Answer"])
            # Display results
            students = len(names)
            final_scores = {
                            "Name": [],
                            "Scores": [],
                            "Reasoning": [],
                            }
            for i in range(students):
                messages = [
                    {"role": "system", "content": "You have to give points to a user-generated answer \
                        based on the following information: \n \
                        This is the question the user tried to answer: " + str(questions) + "\n" +
                        "This is the correct answer: " + str(sample_answer) + "\n" +
                        "The exercise is to be graded out of maximum " + str(max_marks) + " marks \n" + 
                        "These are your instructions on how to give marks: " + str(instructions) + "\n" + 
                        "Only return the number of marks. If there is no answer or it is null, return 0."
                    },
                    {"role": "user", "content": str(answers[i]) if answers[i] != "Nan" else " "}
                ]
                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    temperature=TEMPERATURE,
                    messages=messages,
                )
                marks = int(response.choices[0].message.content)
                final_scores["Name"].append(names[i])
                final_scores["Scores"].append(marks)
                
                messages.append({"role": response.choices[0].message.role, "content": response.choices[0].message.content})
                messages.append({"role": "user", "content": "Please give a reasoning for the marks you assigned"})
                
                # Reasoning
                response = client.chat.completions.create(
                    model="gpt-4-1106-preview",
                    temperature=TEMPERATURE,
                    messages=messages,
                )
                
                final_scores["Reasoning"].append(response.choices[0].message.content)                  
                
            df = pd.DataFrame(final_scores)
            csv = convert_df_to_csv(df=df)
            st.session_state.csv_data = csv
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter valid values for all fields.")
 
# Check if CSV data is available
if st.session_state.csv_data is not None:
    # Create a download button
    st.download_button(
        label="Download CSV",
        data=st.session_state.csv_data,
        file_name="data.csv",
        mime="text/csv",
        disabled=False
    )
else:
    # Display a disabled download button
    st.download_button(
        label="Download CSV",
        data="",
        file_name="data.csv",
        mime="text/csv",
        disabled=True
    )