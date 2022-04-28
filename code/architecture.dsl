workspace "EHR" "This is a model of EHR system" {

    model {

        enterprise ehr {
        
            ehr_system = softwareSystem "EHR System" "EHR & auditing system" {
                ehr_api = container "EHR Rest API" "API for doing EHR operations" "Flask server"
                ca_server = container "Certificate authority server" "Creates certificates that bind user IDs to public keys" "Flask server"
                audit_api = container "Audit Rest API" "API to log and query EHR actions"
                ehr_db = container "EHR database" "Stores all EHRs" "JSON file" "data_storage"
                audit_db = container "Audit log" "A log of all EHR operations" "JSON file" "data_storage"
                pubkey_database = container "Pubkey database" "A database of (public key, User ID) entries" "JSON file" "data_storage"
            }
            
            patient = person "Patient"
            doctor = person "Doctor"
            audit_company = person "Audit company"
            
            patient -> audit_api "Request all EHR actions belonging to this patient"
            doctor -> ehr_api "Add, change, delete or create EHRs"
            audit_company -> ca_server "Request certificate"
            ehr_api -> ehr_db "Read/write EHRs"
            ehr_api -> audit_api "Notify about EHR actions"
            audit_api -> audit_db "Log or get EHR actions"
            patient -> ca_server "Request certificate"
            audit_company -> audit_api "Request all EHR actions belonging to a set of patients"
            ca_server -> pubkey_database "Check/write entries"
        }
    }
    
    views {
        container ehr_system components_architecture somedescription {
            include *
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