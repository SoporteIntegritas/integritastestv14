# -*- coding: utf-8 -*-

from odoo import api, fields, models ,_
from odoo.exceptions import UserError
from datetime import datetime
from odoo.osv import expression


class ACSPatient(models.Model):
    _inherit = 'hms.patient'

    def _rec_count(self):
        rec = super(ACSPatient, self)._rec_count()
        Prescription = self.env['prescription.order']
        Treatment = self.env['hms.treatment']
        for rec in self:
            rec.prescription_count = Prescription.search_count([('patient_id','=',rec.id)])
            rec.treatment_count = Treatment.search_count([('patient_id','=',rec.id)])
            rec.appointment_count = len(rec.appointment_ids)
            rec.evaluation_count = len(rec.evaluation_ids)

    def _acs_get_attachemnts(self):
        attachments = super(ACSPatient, self)._acs_get_attachemnts()
        attachments += self.appointment_ids.mapped('attachment_ids')
        return attachments

    @api.model
    def _get_service_id(self):
        registration_product = False
        if self.env.user.company_id.patient_registration_product_id:
            registration_product = self.env.user.company_id.patient_registration_product_id.id
        return registration_product

    def _get_last_evaluation(self):
        for rec in self:
            evaluation_ids = rec.evaluation_ids.filtered(lambda x: x.state=='done')
                   
            if evaluation_ids:
                rec.last_evaluation_id = evaluation_ids[0].id if evaluation_ids else False
            else:
                rec.last_evaluation_id = False


    ref_doctor_ids = fields.Many2many('res.partner', 'rel_doc_pat', 'doc_id', 
        'patient_id', 'Referring Doctors', domain=[('is_referring_doctor','=',True)])

    #Diseases
    medical_history = fields.Text(string="Past Medical History")
    patient_diseases_ids = fields.One2many('hms.patient.disease', 'patient_id', string='Diseases')

    #Family Form Tab
    genetic_risks_ids = fields.One2many('hms.patient.genetic.risk', 'patient_id', 'Genetic Risks')
    family_history_ids = fields.One2many('hms.patient.family.diseases', 'patient_id', 'Family Diseases History')
    department_ids = fields.Many2many('hr.department', 'patint_department_rel','patient_id', 'department_id',
        domain=[('patient_department', '=', True)], string='Departments')

    medication_ids = fields.One2many('hms.patient.medication', 'patient_id', string='Medications')
    ethnic_group_id = fields.Many2one('acs.ethnicity', string='Ethnic group')
    cod = fields.Many2one('hms.diseases', string='Cause of Death')
    family_member_ids = fields.One2many('acs.family.member', 'patient_id', string='Family')

    prescription_count = fields.Integer(compute='_rec_count', string='# Prescriptions')
    treatment_count = fields.Integer(compute='_rec_count', string='# Treatments')
    appointment_count = fields.Integer(compute='_rec_count', string='# Appointments')
    appointment_ids = fields.One2many('hms.appointment', 'patient_id', 'Appointments')
    medical_alert_ids = fields.Many2many('acs.medical.alert', 'patient_medical_alert_rel','patient_id', 'alert_id',
        string='Medical Alerts')
    registration_product_id = fields.Many2one('product.product', default=_get_service_id, string="Registration Service")
    invoice_id = fields.Many2one("account.move","Registration Invoice")

    evaluation_count = fields.Integer(compute='_rec_count', string='# Evaluations')
    evaluation_ids = fields.One2many('acs.patient.evaluation', 'patient_id', 'Evaluations')

    last_evaluation_id = fields.Many2one("acs.patient.evaluation", string="Last Appointment", compute=_get_last_evaluation, readonly=True)
    weight = fields.Float(related="last_evaluation_id.weight", string='Weight', help="Weight in KG", readonly=True)
    height = fields.Float(related="last_evaluation_id.height", string='Height', help="Height in cm", readonly=True)
    temp = fields.Char(related="last_evaluation_id.temp", string='Temp', readonly=True)
    hr = fields.Char(related="last_evaluation_id.hr", string='HR', help="Heart Rate", readonly=True)
    rr = fields.Char(related="last_evaluation_id.rr", string='RR', readonly=True, help='Respiratory Rate')
    systolic_bp = fields.Char(related="last_evaluation_id.systolic_bp", string="Systolic BP", size=3)
    diastolic_bp = fields.Char(related="last_evaluation_id.diastolic_bp", string="Diastolic BP", size=3)
    spo2 = fields.Char(related="last_evaluation_id.spo2", string='SpO2', readonly=True, 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    bmi = fields.Float(related="last_evaluation_id.bmi", string='Body Mass Index', readonly=True)
    bmi_state = fields.Selection(related="last_evaluation_id.bmi_state", string='BMI State', readonly=True)

    def create_invoice(self):
        product_id = self.registration_product_id or self.env.user.company_id.patient_registration_product_id
        if not product_id:
            raise UserError(_("Please Configure Registration Product in Configuration first."))

        invoice = self.acs_create_invoice(partner=self.partner_id, patient=self, product_data=[{'product_id': product_id}], inv_data={'hospital_invoice_type': 'patient'})
        self.invoice_id = invoice.id

    def action_appointment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_appointment")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id}
        return action

    def action_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id}
        return action

    def action_treatment(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.acs_action_form_hospital_treatment")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id}
        return action

    def action_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_acs_patient_evaluation")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.id, 'default_physician_id': self.primary_doctor.id}
        return action


class ACSFamilyMember(models.Model):
    _name = 'acs.family.member'
    _description= 'Family Member'

    related_patient_id = fields.Many2one('hms.patient', string='Family Member', help='Family Member Name', required=True)    
    patient_id = fields.Many2one('hms.patient', string='Patient')
    relation_id = fields.Many2one('acs.family.relation', string='Relation', required=True)
    inverse_relation_id = fields.Many2one("acs.family.member", string="Inverse Relation")

    def create(self, values):
        res = super(ACSFamilyMember, self).create(values)
        if not res.inverse_relation_id and res.relation_id.inverse_relation_id:
            inverse_relation_id = self.create({
                'inverse_relation_id': res.id,
                'relation_id': res.relation_id.inverse_relation_id.id,
                'patient_id': res.related_patient_id.id,
                'related_patient_id': res.patient_id.id,
            })
            res.inverse_relation_id = inverse_relation_id.id
        return res

    def unlink(self):
        inverse_relation_id = self.mapped('inverse_relation_id')
        res = super(ACSFamilyMember, self).unlink()
        if inverse_relation_id:
            inverse_relation_id.unlink()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: