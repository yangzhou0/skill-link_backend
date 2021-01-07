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
    job_title_uuid = json.load(request)['uuid']
    
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
    #if JSON response is 404 find related jobs... then find skills for those related jobs 


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



@csrf_exempt
def jobs_from_skill_uuids(request):
    # Request is an Object with a key of "uuids" and value is a list of uuids (request may also have value to set to replace number_of_jobs_returned to possibly make amount of jobs returned dynamic based on user selection on front end)
    uuid_list = json.load(request)['uuids']
    job_dict = {}
    job_array = []
    number_of_jobs_returned = 10

    # Nested function that does individual skill to jobs search
    def skill_uuid_to_jobs(skill_uuid):
        url = f'http://api.dataatwork.org/v1/skills/{skill_uuid}/related_jobs'
        response = requests.get(url)
        json_response = response.json()
        job_list = json_response["jobs"]

        return job_list

    # Loops through every uuid in the list that came from request
    for uuid in uuid_list:
        job_list = skill_uuid_to_jobs(uuid)
        # Loops through skill to jobs search and populates dictionary with job title as key and importance of that skill as value
        for job in job_list:
            if job["job_title"] in job_dict:
                job_dict[job["job_title"]] += job["importance"]
            else:
                job_dict[job["job_title"]] = job["importance"]

    # After all skill to job search values (importance) have been added to dict, loop through job_dict and populate list with requested amount of jobs to list (number_of_jobs_returned)
    for job in job_dict:
        if len(job_array) < number_of_jobs_returned:
            job_array.append({job:job_dict[job]})

        # Once number_of_jobs_returned lenght is met, continue to loop through job_dict and compare importance score with scores already in job_list, goal is to populate job list with a number of highest importance values/job titles equal to number_of_jobs_returned
        else:
            lowest_score = list(job_array[0].values())[0]
            index = 0
            add_new = False
            for job_index in range(len(job_array)):
                if list(job_array[job_index].values())[0] < lowest_score:
                    index = job_index
                    lowest_score = list(job_array[job_index].values())[0]
                if list(job_array[job_index].values())[0] < job_dict[job]:
                    add_new = True
            if add_new:
                job_array[index] = {job:job_dict[job]}

    #return job_array
    return JsonResponse(data=job_array, status=200, safe=False)

# testy_test is variable to test function for the time being
# testy_test =["6ae28a55456b101be8261e5dee44cd3e", "d1715efc5a67ac1c988152b8136e3dfa","1cea5345d284f36245a94301b114b27c","a636cb69257dcec699bce4f023a05126","2c77c703bd66e104c78b1392c3203362"]


#still working on autofill/possible database solution for skill searching
#limits return skills to abilities
def get_those_skills():
    offset = 0
    skill_dict = {}
    counter = 0

    for i in range(55):
        url = f'http://api.dataatwork.org/v1/skills?offset={offset}&limit=500'
        response = requests.get(url)
        json_response = response.json()
        offset += 500
        for skill in json_response:
            if not 'links' in skill:
                if skill['type'] and skill['type'] != "tool":
                    skill_dict[skill["name"]] = skill["uuid"]
                    counter+=1
        print(offset)
    print(counter)
    return skill_dict