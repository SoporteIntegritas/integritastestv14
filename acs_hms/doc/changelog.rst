`1.0.10                                                       [19/02/2021]`
***************************************************************************
- Imprvoed code for allowing manuly entry for prescription qty.

`1.0.9                                                       [12/02/2021]`
***************************************************************************
- Imprvoed code for followup conf on HMS setting.

`1.0.8                                                       [10/02/2021]`
***************************************************************************
- Fix issue of prescripion send by mail template issue.

`1.0.7                                                       [02/02/2021]`
***************************************************************************
- Set default timer propelry on change of physician nnd set dureation on 
change of end date.

`1.0.6                                                       [29/01/2021]`
***************************************************************************
- Updated Translated File.
- Add option to create patient from partner.

`1.0.5                                                       [25/01/2021]`
***************************************************************************
- Updated Search View.

`1.0.4                                                       [09/01/2020]`
***************************************************************************
- Added proper genetic risk view and menu.

`1.0.3                                                       [11/11/2020]`
***************************************************************************
- Search Precsription by medicine name.

`1.0.2                                                        [29/10/2020]`
***************************************************************************
- Add invoice ref and origin also on insurance invoice.

`1.0.1                                                        [10/10/2020]`
***************************************************************************
- Launched Module for v14 with following changes.

Patient:
- Rename patient_diseases to patient_diseases_ids
- Rename genetic_risks to genetic_risks_ids
- Rename family_history to family_history_ids

Physician:
- Rename government_id to medical_license
- Rename specialty to specialty_id

Appointment:
- replace diseas_id by diseases_ids
- Add auotmatic next followup date

Prescription:
- replace diseas_id by diseases_ids

Deaprtment:
- replace patient_department by patient_department
- Added department_type to manage appointment types.

Add option to print Qr on prescription for authentication.
Add option to manage planning date and duration on appoitnment.
Add new department_type to manage diff dipartment types in speciality.
Add new Evaluation Object.

Split module with acs_hms_base and move Patient, Physician and Drug 
related code in that module