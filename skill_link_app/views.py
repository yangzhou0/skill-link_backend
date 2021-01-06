from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

''' v Autocomplete feature will be ran on the front end v '''
# JOB_UUID_DICT = {}

# user_input = 'software'

# def job_auto_complete(request):
#     #Job Title Autocomplete CONTAINS
#     #Returns a list of job title suggestions for Autocomplete feature

#     #Compile HTTP GET Request
#     job_title_uuid_lst = []
#     job_title_suggestion_lst = []
#     url = f'http://api.dataatwork.org/v1/jobs/autocomplete?contains={user_input}'
#     response = requests.get(url)
#     print(response)

#     #Convert GET request to JSON
#     json_response = response.json()

#     #Unpack JSON for the Job Title Suggestion's UUID and save to a list
#     #Unpack JSON for Autocomplete Suggestions and save them to a list
#     for i in range(len(json_response)):
#         job_title_uuid_lst.append(json_response[i]['uuid'])
#         job_title_suggestion_lst.append(json_response[i]['suggestion'])
    
#     #Dictionary of Job Title as KEYs and UUIDs as VALUEs
#     #To be used in a subsequent function
#     JOB_UUID_DICT = dict(zip(job_title_suggestion_lst, job_title_uuid_lst))

#     #Example of output (A list of job title suggestions)
#     #print(job_title_suggestion_lst)
#     return JsonResponse(data=job_title_suggestion_lst, status=200, safe=False)
''' ^ Autocomplete feature will be ran on the front end ^ '''


@csrf_exempt
def job_title_to_skills(request):
    #Input is a UUID for Job Title
    #Output is an object containing skill_list, ability_list and knowledge_list


    #SAMPLE SEED DATA
    #job_title = 'Software Engineer'
    #JOB_UUID_DICT = {'Software Engineer': '4b7281a983a4574eb887d29f7fbebd88'}

    #Unpack incoming JSON for job_title_uuid
    job_title_uuid = json.load(request)['job-title']
    print('XXXXXXXXXX',job_title_uuid)
    

    #FUNCTION OUTPUT (before API data is added)
    skill_ability_knowledge_obj = {
        "skill_list" : [],
        "ability_list" : [],
        "knowledge_list": []
    }

    #Compile HTTP GET Request
    url = f'http://api.dataatwork.org/v1/jobs/{job_title_uuid}/related_skills'
    response = requests.get(url)

    #Convert the GET API call to JSON
    json_response = response.json()

    #Isolate JSON to only skill data
    skill_list = json_response["skills"]

    #Write top 5 skills/ability/knowledge to skill_ability_knowledge_obj
    for i in range(len(skill_list)):
        if skill_list[i]["skill_type"] == "skill" and len(skill_ability_knowledge_obj["skill_list"]) < 5:
                skill_ability_knowledge_obj["skill_list"].append(
                    skill_list[i]["skill_name"])


        elif skill_list[i]["skill_type"] == "ability" and len(skill_ability_knowledge_obj["ability_list"]) < 5:
                skill_ability_knowledge_obj["ability_list"].append(
                    skill_list[i]["skill_name"])


        elif skill_list[i]["skill_type"] == "knowledge" and  len(skill_ability_knowledge_obj["knowledge_list"]) < 5:
                skill_ability_knowledge_obj["knowledge_list"].append(
                    skill_list[i]["skill_name"])
    
    return JsonResponse(data=skill_ability_knowledge_obj, status=200, safe=False)