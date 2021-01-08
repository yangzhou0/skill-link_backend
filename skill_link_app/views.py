from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

@csrf_exempt
def job_title_to_skills(request):
    #Input is a UUID for Job Title
    #Output is an object containing skill_list, ability_list and knowledge_list

    #SAMPLE SEED DATA
    #job_title = 'Software Engineer'
    #{'Software Engineer': '4b7281a983a4574eb887d29f7fbebd88'}
    
    #FUNCTION OUTPUT (before API data is added)
    skill_ability_knowledge_obj = {
        "skill_list" : [],
        "ability_list" : [],
        "knowledge_list": []
    }
    
    #Unpack incoming JSON for job_title_uuid
    job_title_uuid = json.load(request)['uuid']

    #Compile HTTP GET Request
    response = requests.get(
        f'http://api.dataatwork.org/v1/jobs/{job_title_uuid}/related_skills')
    
    if response.status_code == 404:
        print('response.status_code == 404 - NOW HANDLING EXCEPTION')

        #Find the job title for the job_title_uuid passed from the front end
        response = requests.get(
            f'http://api.dataatwork.org/v1/jobs/{job_title_uuid}')
        json_response = response.json()

        #Extract first and last word in job title
        job_title_word_list = json_response['title'].split(' ')
        first_word_job_title = job_title_word_list[0]
        last_word_job_title = job_title_word_list[-1]

        #Get assosciated jobs for first word of job title
        firstword_assosciated_jobs = requests.get(
            f'http://api.dataatwork.org/v1/jobs/autocomplete?begins_with={first_word_job_title}').json()

        #Get assosciated jobs for last word of job title
        lastword_assosciated_jobs = requests.get(
            f'http://api.dataatwork.org/v1/jobs/autocomplete?ends_with={last_word_job_title}').json()
        
        #Iterate through firstword_assosciated_jobs for job UUIDs and send API requests until status_code is 200
        #Results are ordered by strongest assosciations so the first job UUID to return 200 code will be strongest match
        first_word_related_skills = ''
        for i in range(len(firstword_assosciated_jobs)):
            response = requests.get(
                f'http://api.dataatwork.org/v1/jobs/{firstword_assosciated_jobs[i]["uuid"]}/related_skills')
            if response.status_code == 200:
                first_word_related_skills = (response.json())
                break
        
        #Iterate through lastword_assosciated_jobs for job UUIDs and send API requests until status_code is 200
        #Results are ordered by strongest assosciations so the first job UUID to return 200 code will be strongest match
        last_word_related_skills = ''
        for i in range(len(lastword_assosciated_jobs)):
            response = requests.get(
                f'http://api.dataatwork.org/v1/jobs/{lastword_assosciated_jobs[i]["uuid"]}/related_skills')
            if response.status_code == 200:
                last_word_related_skills = (response.json())
                break

        #Isolate JSON to only skill data
        first_word_skill_list = first_word_related_skills["skills"]

        #Write best 3 skills, 2 ability, 3 knowledge to skill_ability_knowledge_obj
        for i in range(len(first_word_skill_list)):
            if (first_word_skill_list[i]["skill_type"] == "skill" and
            len(skill_ability_knowledge_obj["skill_list"]) < 3):
                    skill_ability_knowledge_obj["skill_list"].append(
                        first_word_skill_list[i]["skill_name"])
        
            elif (first_word_skill_list[i]["skill_type"] == "ability" and
            len(skill_ability_knowledge_obj["ability_list"]) < 2):
                    skill_ability_knowledge_obj["ability_list"].append(
                        first_word_skill_list[i]["skill_name"])

            elif (first_word_skill_list[i]["skill_type"] == "knowledge" and
            len(skill_ability_knowledge_obj["knowledge_list"]) < 3):
                    skill_ability_knowledge_obj["knowledge_list"].append(
                        first_word_skill_list[i]["skill_name"])
        
        #Isolate JSON to only skill data
        last_word_skill_list = last_word_related_skills["skills"]

        #Write best 2 skills, 3 ability, 2 knowledge to skill_ability_knowledge_obj to a total of 5 items per list
        for i in range(len(last_word_skill_list)):
            if (last_word_skill_list[i]["skill_type"] == "skill" and 
            len(skill_ability_knowledge_obj["skill_list"]) < 5):
                    skill_ability_knowledge_obj["skill_list"].append(
                        last_word_skill_list[i]["skill_name"])
        
            elif (last_word_skill_list[i]["skill_type"] == "ability" and
            len(skill_ability_knowledge_obj["ability_list"]) < 5):
                    skill_ability_knowledge_obj["ability_list"].append(
                        last_word_skill_list[i]["skill_name"])

            elif (last_word_skill_list[i]["skill_type"] == "knowledge" and
            len(skill_ability_knowledge_obj["knowledge_list"]) < 5):
                    skill_ability_knowledge_obj["knowledge_list"].append(
                        last_word_skill_list[i]["skill_name"])

        return JsonResponse(data=skill_ability_knowledge_obj, status=200, safe=False)

    elif response.status_code == 200:
        #Convert API call to JSON
        json_response = response.json()

        #Isolate JSON to only skill data
        skill_list = json_response["skills"]

        #Write top 5 skills/ability/knowledge to skill_ability_knowledge_obj
        for i in range(len(skill_list)):
            if (skill_list[i]["skill_type"] == "skill" and
            len(skill_ability_knowledge_obj["skill_list"]) < 5):
                    skill_ability_knowledge_obj["skill_list"].append(
                        skill_list[i]["skill_name"])

            elif (skill_list[i]["skill_type"] == "ability" and
            len(skill_ability_knowledge_obj["ability_list"]) < 5):
                    skill_ability_knowledge_obj["ability_list"].append(
                        skill_list[i]["skill_name"])

            elif (skill_list[i]["skill_type"] == "knowledge" and
            len(skill_ability_knowledge_obj["knowledge_list"]) < 5):
                    skill_ability_knowledge_obj["knowledge_list"].append(
                        skill_list[i]["skill_name"])
        
        return JsonResponse(data=skill_ability_knowledge_obj, status=200, safe=False)
    
    else:
        skill_ability_knowledge_obj = {
        "skill_list" : ["Oops something went wrong!"],
        "ability_list" : ["Oops something went wrong!"],
        "knowledge_list": ["Oops something went wrong!"]
        }
        return JsonResponse(data=skill_ability_knowledge_obj,status=200, safe=False)


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