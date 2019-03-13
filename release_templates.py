
def get_release_templates(ID,start_date,end_date):
    releaseTemplates=[
        {
    "release_phase": {
        "name": "Analyse High-Level Requirements",
        "phase_type": "phase",
        "release_id": ID,
        "start_on": start_date,
        "end_on": end_date
    }
    },

    {
    "release_phase": {
        "name": "Document Scope",
        "phase_type": "phase",
        "release_id": ID,
        "start_on": start_date,
        "end_on": end_date
    }
    },


    {
    "release_phase": {
        "name": "Finalize Project Deliverables",
        "phase_type": "milestone",
        "release_id": ID,
        "start_on": start_date,
        "end_on": end_date
    }
    },

    {
    "release_phase": {
        "name": "UX Design",
        "phase_type": "phase",
        "release_id": ID,
        "start_on": start_date,
        "end_on": end_date
    }
    },

    {
    "release_phase": {
        "name": "Development",
        "phase_type": "phase",
        "release_id": ID,
        "start_on": start_date,
        "end_on": end_date
    }
    },

    {
    "release_phase": {
        "name": "Launch Planning",
        "phase_type": "phase",
        "release_id": ID,
        "start_on": start_date,
        "end_on": end_date
    }
    }




    ]
    return releaseTemplates