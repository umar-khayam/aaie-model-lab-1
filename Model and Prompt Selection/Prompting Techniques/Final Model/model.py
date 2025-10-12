from utlis.prompt import *
import json
import os
import re
import google.generativeai as genai

# Set your API key (from Google AI Studio / Cloud console)

# Choose model: "gemini-1.5-pro" or "gemini-1.5-flash"




def generated_response_gemini(message):
    model = genai.GenerativeModel("gemini-1.5-flash",system_instruction= message['system'])
    chat = model.start_chat()
    response = chat.send_message(message['user'])
    return response.text

#The input include:
#- training_data: the path to training data
#- domain: the domain knowledge for the submission
#- submission: the submission of the student
def process_single_submission(args):
    training_data = './TrainingData' #The training data PATH
    domain = args.get('domain')
    submission = args.get('submission')

    
    #Load the domain file
    file = training_data + domain + '.json' 
    with open(file, 'r') as file:
        data = json.load(file) #Get the data file

    #Get the rubric of the domain
    rubric = format_rubric(data['rubric'])
    #Get some few shot example
    example = create_few_shot_block(data['submissions'])
    
    detector_prompt = build_detection_prompt(submission = submission, example = example) #AI dection prompt
    feedback_prompt = build_feedback_prompt(submission = submission, rubric = rubric) #Feedback generation AI


    # Run AI Detector and Feedback AI
    ai_pred, _ = generated_response_gemini(message= detector_prompt)
    feedback_result = generated_response_gemini(message= feedback_prompt)

    #Save the result
    result = {"ai_detection": { "text": submission, "predictions": ai_pred },
              "feedback_ai": {"text": submission, "generated_text": feedback_result}}
    return result
    

if __name__ == "__main__":
    args = {
        "domain": "engineering",
        "submission": "This is a sample student submission to test the AI."
    }
    genai.configure(api_key="")
    output = process_single_submission(args)
    print(json.dumps(output, indent=2))