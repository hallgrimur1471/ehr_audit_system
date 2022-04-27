workspace "EHR" "This is a model of EHR system" {

    model {

        enterprise ehr {
        
            ehr_system = softwareSystem "EHR System" "EHR & auditing system" {
                ehr_api = container "EHR Rest API" "API for doing EHR operations" "Flask server"
                ehr_db = container "EHR database" "Stores all EHRs" "JSON file" "data_storage"
                audit_db = container "Audit log" "A log of all EHR operations" "JSON file" "data_storage"
                audit_api = container "Audit Rest API" "API for querying EHR actions"
            }
            
            doctor = person "Doctor"
            patient = person "Patient"
            audit_company = person "Audit company"
            
            doctor -> ehr_api "Add, change, delete or create EHRs"
            ehr_api -> ehr_db "Read/write EHRs"
            ehr_api -> audit_db "Log EHR actions"
            audit_api -> audit_db "Get EHR actions"
            patient -> audit_api "Request all EHR actions belonging to this patient"
            audit_company -> audit_api "Request all EHR actions belonging to a set of patients"
        }
    }
    
    views {
        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            element "data_storage" {
                shape Cylinder
            }
        }
    }
}