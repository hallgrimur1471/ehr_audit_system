# EHR Audit System

This repository is a prototype of a Electronic health record (EHR) system. All access requests are recoreded in a log file for later audit on access history. The system tries to fulfill the following goals:

1. **Privacy**: Patient privacy should be maintained. Unauthorized entities should not be able to access audit records.
2. **Identification and authorization**: All system users must be identified and authenticated. All requests to access the audit data should be authorized.
3. **Queries**: Authorized entities should be able to query audit records.
4. **Immutability**: No one should be able to delete or change existing audit records without detection. Any modifications/deletions of the audit records should be detected and reported.
5. **Decentralization**: The system should not rely on a single trusted entity to support immutability.

This project and the system goals was specified by my instructor in the course CSCI531 at USC as a final project of the course.
