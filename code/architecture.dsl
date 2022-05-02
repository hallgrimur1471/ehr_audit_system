workspace "EHR" "This is a model of EHR system" {

    model {

        enterprise ehr {
        
            ehr_system = softwareSystem "EHR System" "EHR & auditing system" {
                ehr_api = container "EHR Rest API" "API for doing EHR operations" "Flask server"
                ehr_client = container "EHR application" "Client program to do EHR operations" "Python CLI program"
                audit_client = container "Audit application" "Client program to audit EHR action history" "Python CLI program"
                audit_api = container "Audit Rest API" "API to log and query EHR actions"
                ehr_db = container "EHR database" "Stores all EHRs" "JSON file" "data_storage"
                audit_db = container "Audit log" "An encrypted log of all EHR actions" "JSON file" "data_storage"
            }
            
            patient = person "Patient"
            doctor = person "Doctor"
            audit_company = person "Audit company"
            
            patient -> audit_client "Request all EHR actions belonging to this patient"
            doctor -> ehr_client "Add, change, delete or create EHRs"
            ehr_client -> ehr_api "Requests to add, change, delete or create EHRs"
            ehr_api -> ehr_db "Read/write EHRs"
            ehr_api -> audit_api "Notify about EHR actions"
            audit_client -> audit_api "Fetch encrypted EHR actions belonging to patient"
            audit_api -> audit_db "Log or get encrypted EHR actions"
            audit_company -> audit_client "Request all EHR actions belonging to a patients"
        }
    }
    
    views {
        container ehr_system components_architecture somedescription {
            include *
            autoLayout tb
        }
        
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