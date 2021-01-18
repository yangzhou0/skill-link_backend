from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import re

#HELPER FUNCTION
def video_link_maker(job_video):
    video_code = job_video[-13:-5]
    iframe = f"<iframe src='http://www.careeronestop.org/videos/Careeronestop-videos-content.aspx?videocode={video_code}' width='560' height='315' frameborder='0' scrolling='no' allowfullscreen/>"
    return iframe

@csrf_exempt
def all_job_data(request):
    #Input: job_title and UUID and zipcode 
    ##Output: an object of all necessary job data

    #Seed Data
    # zipcode = "10001"
    # job_title = "Nuclear Engineers"
   
    incoming_job_data = json.load(request)
    job_title = incoming_job_data["job_title"]
    zipcode = incoming_job_data["zipcode"]
    
    #Make job_title compatible with API
    job_title = job_title.replace(' ', '%20')
    
    
    #FUNCTION OUTPUT (before API data is added)
    result = {
        "job_description" : "",
        "job_median_annual_salary" : "",
        "job_video" : "",
        "related_occupations" : [], 
        "daily_activities": [],
        "knowledge_list" : [],
        "abilities_list" : [],
        "skills_list" : []
    }
    
    #Variables to reused:
    headers = {"Authorization": "Bearer +h3F09pWZZGpREt8CJ15xFwJIgVHTPzMzmki22tnMRPHuVnoYy8W6a2MI3xLfXZPF3nM6DBqoSyc5aRfnThtBg=="}

    #Get Occupation Details
    occupation_details_url = f'https://api.careeronestop.org/v1/occupation/wsDcyeU9muW1AxN/{job_title}/{zipcode}?training=true&interest=false&videos=true&tasks=false&dwas=true&wages=true&alternateOnetTitles=true&projectedEmployment=true&ooh=false&stateLMILinks=false&relatedOnetTitles=true&skills=true&knowledge=true&ability=true&trainingPrograms=true'

    occupation_details_response = requests.get(occupation_details_url, headers=headers)
    occupation_details_json = occupation_details_response.json()

    for i in range(len(occupation_details_json["OccupationDetail"])):
        result["job_description"] = occupation_details_json["OccupationDetail"][i]['OnetDescription']
        result["job_video"] = video_link_maker(occupation_details_json["OccupationDetail"][i]["COSVideoURL"])
        result["daily_activities"].append(occupation_details_json["OccupationDetail"][i]["Dwas"][0]["DwaTitle"])
        result["daily_activities"].append(occupation_details_json["OccupationDetail"][i]["Dwas"][1]["DwaTitle"])
    
    if occupation_details_json["OccupationDetail"][0]["Wages"]["NationalWagesList"][0]['RateType'] == "Annual":
        result["job_median_annual_salary"] = occupation_details_json["OccupationDetail"][0]["Wages"]["NationalWagesList"][0]['Median']
    else:
        result["job_median_annual_salary"] = occupation_details_json["OccupationDetail"][0]["Wages"]["NationalWagesList"][1]['Median']

    #Get related occupations and append to related occupations list in result object
    related_titles = occupation_details_json["OccupationDetail"][0]["RelatedOnetTitles"]
    dictionary_counter = 0
    for title in related_titles:
        result["related_occupations"].append(related_titles[title])
        dictionary_counter += 1 
        if dictionary_counter == 3:
            dictionary_counter = 0
            break


    #Get knowledge/skills/abilities and append to respective list in result object
    result["knowledge_list"].append(occupation_details_json["OccupationDetail"][0]["KnowledgeDataList"][0]['ElementName'])
    result["knowledge_list"].append(occupation_details_json["OccupationDetail"][0]["KnowledgeDataList"][1]['ElementName'])
    result["abilities_list"].append(occupation_details_json["OccupationDetail"][0]["AbilityDataList"][0]['ElementName'])
    result["abilities_list"].append(occupation_details_json["OccupationDetail"][0]["AbilityDataList"][1]['ElementName'])
    result["skills_list"].append(occupation_details_json["OccupationDetail"][0]["SkillsDataList"][0]['ElementName'])
    result["skills_list"].append(occupation_details_json["OccupationDetail"][0]["SkillsDataList"][1]['ElementName'])


    print(result)
    return JsonResponse(data=result, status=200, safe=False)

@csrf_exempt
def learning_resources(request):
    #INPUT: job_title, zipcode
    #OUTPUT: an object of learning resources, unique to each job_tile and zipcode
    result = {
    "school_programs" : [], 
    "ebook_list" : [], #NOT BUILT
    }
    #SEED DATA:
    # job_title = "Statisticians"
    # zipcode = "11101"
    incoming_job_data = json.load(request)
    job_title = incoming_job_data["job_title"]
    zipcode = incoming_job_data["zipcode"]
    
    #Get school programs
    school_programs_url = f"https://api.careeronestop.org/v1/training/wsDcyeU9muW1AxN/{job_title}/{zipcode}/25/0/0/0/0/0/0/0/0/10"
    headers = {
        "Authorization": 
        "Bearer +h3F09pWZZGpREt8CJ15xFwJIgVHTPzMzmki22tnMRPHuVnoYy8W6a2MI3xLfXZPF3nM6DBqoSyc5aRfnThtBg=="
    }

    school_programs_response = requests.get(school_programs_url, headers=headers)
    school_programs_json = school_programs_response.json()

    #Append school program data to result
    for i in range(len(school_programs_json["SchoolPrograms"])):
        place = {}
        school_program = school_programs_json["SchoolPrograms"][i]
        place["school_name"] = school_program["SchoolName"]
        place["program_name"] = school_program["ProgramName"]
        place["address"] = school_program["Address"] + ' ' + school_program["City"] + ' ' + school_program["StateAbbr"] + ' ' + school_program["Zip"]
        #Fix bad phone numbers - REFACTOR LATER
        if len(school_program["Phone"]) > 10:
            place["phone"] = school_program["Phone"][:10]
        else:
            place["phone"] = school_program["Phone"]

        #Fix missing URL prefixes
        if school_program["SchoolUrl"][0:8] != "https://":
            place["school_url"] = 'https://' + school_program["SchoolUrl"]
        else:
            place["school_url"] = school_program["SchoolUrl"]
        
        result["school_programs"].append(place)
    
    #Fix URL suffix
    for i in range(len(result["school_programs"])):
        school_program = result["school_programs"][i]
        if school_program["school_url"][-1] == '/':
            school_program["school_url"] = school_program["school_url"][:-1]

    #Use regex to extract domain and top level domain, to be sent to favicon grabber API
    for i in range(len(result["school_programs"])):
        school_program = result["school_programs"][i]
        #print('LINE 125',school_program["school_url"])
        match = re.findall(r'(\w+\.\w+)$', school_program["school_url"])
        #print('LINE 127 MATCH=', match)
        #If REGEX match is found for domain and top level domain, img_url will be set equal to its icon url
        if len(match) > 0:
            icon_response = requests.get(f'http://favicongrabber.com/api/grab/{match[0]}')
            if icon_response.status_code == 200:
                icon_response = icon_response.json() #Convert favicon grabber API response to json
                school_program["img_url"] = icon_response["icons"][0]["src"]  #Parse through json for its icon url, and write to the result

            #If no icon can be found, img_url will be set equal to its status code
            else:
                print('No icon can be found for:', match[0], '...', 'STATUS_CODE:', icon_response.status_code)
                school_program["img_url"] = icon_response.status_code
                

        #If no REGEX match is found for domain and top level domain, img_url will be set equal to 404
        else: 
            print('No REGEX match could be found for', school_program["school_url"])
            school_program["img_url"] = 404
         
    return JsonResponse(data=result, status=200, safe=False)


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