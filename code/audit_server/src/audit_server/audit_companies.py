COMPANY_PATIENTS = {"usc": ["alice", "bob", "eve"], "ucla": ["carol", "david"]}


def get_company_of(patient):
    for company, patients in COMPANY_PATIENTS.items():
        if patient in patients:
            return company
    raise RuntimeError("Patient not found")


def get_patients(company):
    return COMPANY_PATIENTS[company]


def get_companies():
    return [k for k, v in COMPANY_PATIENTS.items()]
