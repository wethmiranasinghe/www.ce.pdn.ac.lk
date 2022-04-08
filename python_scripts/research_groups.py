'''
------------------------------------------------------------------------------

This  script will read the file, '/edit/research-groups.json', pre-process and
save the research group details in the folder, '/_data/research_groups'.

------------------------------------------------------------------------------
'''

import requests
import json
import os

# Where the API is available
apiBase = "https://api.ce.pdn.ac.lk"

studentSource = apiBase + "/people/v1/students/all/"
staffSource = apiBase + "/people/v1/staff/all/"
projectSource = apiBase + "/projects/v1/all/"

def getStud_profile(data):
    # TODO: Check the name options
    if(data['name_with_initials'] != ""):
        name = data["name_with_initials"]
    elif(data['preferred_long_name'] != ""):
        name = data["preferred_long_name"]
    elif(data['full_name'] != ""):
        name = data["full_name"]
    else:
        # Name not found
        return {}

    if (data["honorific"] != ""):
        name = data["honorific"] + " " + name

    return {
        "name": name,
        "affiliation": data["current_affiliation"],
        "profile_url": data["profile_page"],
        "profile_image": data["profile_image"]
    }

def getStaff_profile(data):
    return {
        "name": data["name"],
        "affiliation": "Department of Computer Engineering, University of Peradeniya",
        "profile_url": data["profile_url"],
        "profile_image": data["profile_image"]
    }

# ------------------------------------------------------------------------------
# Collect Local/Remote Data
# ------------------------------------------------------------------------------

# Gather Student API data
student_dict = {}
req_students = requests.get(studentSource)
if req_students.status_code==200:
    student_dict = json.loads(req_students.text)

# Gather Staff API data
staff_dict = {}
req_staff = requests.get(staffSource)
if req_staff.status_code==200:
    staff_dict = json.loads(req_staff.text)

    # # Gather Project API data
    # req_projects = requests.get(projectSource)
    # if req_projects.status_code==200:
    #     projects = json.loads(req_projects.text)

# Gather Research Group Data
researchgroup_file = open("../edit/research-groups.json")
research_groups = json.load(researchgroup_file)

# ------------------------------------------------------------------------------
# Pre Process the Data
# ------------------------------------------------------------------------------
for group in research_groups:
    # print(json.dumps(group, indent = 4))

    formatted_group = group.copy()
    # print(group['shortCode'])

    # Update contact with details
    # NOTE: This is only works with the Staff Members yet
    formatted_group['contact'] = []

    for c in group['contact']:
        contact = c.split('@')[0]
        # print(contact)
        if contact in staff_dict:
            # print(staff_dict[contact])
            formatted_group['contact'].append(getStaff_profile(staff_dict[contact]))
            # print(formatted_group['contact'])


    # Update maintainers with details
    # NOTE: This is works with the Students and Staff yet
    formatted_group['maintainers'] = []

    for m in group['maintainers']:
        maintainer = m.split('@')[0]
        # print(student)
        if maintainer in student_dict:
            formatted_group['maintainers'].append(getStud_profile(student_dict[maintainer]))

        elif maintainer in staff_dict:
            formatted_group['maintainers'].append(getStaff_profile(staff_dict[maintainer]))
    # print(formatted_group['maintainers'])


    # NOTE: This is works with the Students and Staff yet
    formatted_group['people'] = {
        'staff': [],
        'students': [],
        'external-collaborators': group['people']['external-collaborators']
    }

    for p in group['people']['staff']:
        person = p.split('@')[0]
        # print(student)
        if person in staff_dict:
            formatted_group['people']['staff'].append(getStaff_profile(staff_dict[person]))

    for p in group['people']['students']:
        person = p
        # print(student)
        if person in student_dict:
            formatted_group['people']['students'].append(getStud_profile(student_dict[person]))
    # print(formatted_group['maintainers'])



    filename = "../_data/research_groups/{0}.json".format(group['shortCode'])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        f.write(json.dumps(formatted_group, indent = 4))
