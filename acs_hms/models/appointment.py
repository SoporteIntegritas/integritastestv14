# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class AppointmentPurpose(models.Model):
    _name = 'appointment.purpose'
    _description = "Appointment Purpose"

    name = fields.Char(string='Appointment Purpose', required=True, translate=True)


class AppointmentCabin(models.Model):
    _name = 'appointment.cabin'
    _description = "Appointment Cabin"

    name = fields.Char(string='Appointment Cabin', required=True, translate=True)


class Appointment(models.Model):
    _name = 'hms.appointment'
    _description = "Appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'acs.hms.mixin', 'acs.documnt.mixin']
    _order = "id desc"

    @api.model
    def _get_service_id(self):
        consultation = False
        if self.env.user.company_id.consultation_product_id:
            consultation = self.env.user.company_id.consultation_product_id.id
        return consultation

    @api.depends('medical_alert_ids')
    def _get_alert_count(self):
        for rec in self:
            rec.alert_count = len(rec.medical_alert_ids)

    @api.depends('patient_id', 'patient_id.birthday', 'date')
    def get_patient_age(self):
        for rec in self:
            age = ''
            if rec.patient_id.birthday:
                end_data = rec.date or fields.Datetime.now()
                delta = relativedelta(end_data, rec.patient_id.birthday)
                if delta.years <= 2:
                    age = str(delta.years) + _(" Year") + str(delta.months) + _(" Month ") + str(delta.days) + _(" Days")
                else:
                    age = str(delta.years) + _(" Year")
            rec.age = age

    def _get_evaluation(self):
        for rec in self:
            rec.evaluation_id = rec.evaluation_ids[0].id if rec.evaluation_ids else False

    READONLY_STATES = {'cancel': [('readonly', True)], 'done': [('readonly', True)]}

    name = fields.Char(string='Appointment Id', readonly=True, copy=False, tracking=True, states=READONLY_STATES)
    patient_id = fields.Many2one('hms.patient', ondelete='restrict',  string='Patient',
        required=True, index=True,help='Patient Name', states=READONLY_STATES, tracking=True)
    image_128 = fields.Binary(related='patient_id.image_128',string='Image', readonly=True)
    physician_id = fields.Many2one('hms.physician', ondelete='restrict', string='Physician', 
        index=True, help='Physician\'s Name', states=READONLY_STATES, tracking=True)
    department_id = fields.Many2one('hr.department', ondelete='restrict', 
        domain=[('patient_department', '=', True)], string='Department', tracking=True, states=READONLY_STATES)
    no_invoice = fields.Boolean(string='Invoice Exempt', states=READONLY_STATES)
    follow_date = fields.Datetime(string="Follow Up Date", states=READONLY_STATES)
    
    evaluation_ids = fields.One2many('acs.patient.evaluation', 'appointment_id', 'Evaluations')
    evaluation_id = fields.Many2one('acs.patient.evaluation', ondelete='restrict', compute=_get_evaluation,
        string='Evaluation', states=READONLY_STATES)

    weight = fields.Float(related="evaluation_id.weight", string='Weight', help="Weight in KG", states=READONLY_STATES)
    height = fields.Float(related="evaluation_id.height", string='Height', help="Height in cm", states=READONLY_STATES)
    temp = fields.Char(related="evaluation_id.temp", string='Temp', states=READONLY_STATES)
    hr = fields.Char(related="evaluation_id.hr", string='HR', help="Heart Rate", states=READONLY_STATES)
    rr = fields.Char(related="evaluation_id.rr", string='RR', states=READONLY_STATES, help='Respiratory Rate')
    systolic_bp = fields.Char(related="evaluation_id.systolic_bp", string="Systolic BP", size=3, states=READONLY_STATES)
    diastolic_bp = fields.Char(related="evaluation_id.diastolic_bp", string="Diastolic BP", size=3, states=READONLY_STATES)
    spo2 = fields.Char(related="evaluation_id.spo2", string='SpO2', states=READONLY_STATES, 
        help='Oxygen Saturation, percentage of oxygen bound to hemoglobin')
    bmi = fields.Float(related="evaluation_id.bmi", string='Body Mass Index', store=True)
    bmi_state = fields.Selection(related="evaluation_id.bmi_state", string='BMI State', store=True)

    differencial_diagnosis = fields.Text(string='Differential Diagnosis', states=READONLY_STATES, help="The process of weighing the probability of one disease versus that of other diseases possibly accounting for a patient's illness.")
    medical_advice = fields.Text(string='Medical Advice', states=READONLY_STATES, help="The provision of a formal professional opinion regarding what a specific individual should or should not do to restore or preserve health.")
    chief_complain = fields.Text(string='Chief Complaints', states=READONLY_STATES, help="The concise statement describing the symptom, problem, condition, diagnosis, physician-recommended return, or other reason for a medical encounter.")
    present_illness = fields.Text(string='History of Present Illness', states=READONLY_STATES)
    lab_report = fields.Text(string='Lab Report', states=READONLY_STATES, help="Details of the lab report.")
    radiological_report = fields.Text(string='Radiological Report', states=READONLY_STATES, help="Details of the Radiological Report")
    notes = fields.Text(string='Notes', states=READONLY_STATES)
    past_history = fields.Text(string='Past History', states=READONLY_STATES, help="Past history of any diseases.")
    invoice_id = fields.Many2one('account.move', string='Invoice')
    urgency = fields.Selection([
            ('normal', 'Normal'),
            ('urgent', 'Urgent'),
            ('medical_emergency', 'Medical Emergency'),
        ], string='Urgency Level', default='normal', states=READONLY_STATES)
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('waiting', 'Waiting'),
            ('in_consultation', 'In consultation'),
            ('pause', 'Pause'),
            ('to_invoice', 'To Invoice'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ], string='State',default='draft', required=True, copy=False, tracking=True,
        states=READONLY_STATES)
    product_id = fields.Many2one('product.product', ondelete='restrict', 
        string='Consultation Service', help="Consultation Services", 
        domain=[('hospital_product_type', '=', "consultation")], required=True, 
        default=_get_service_id, states=READONLY_STATES)
    age = fields.Char(compute="get_patient_age", string='Age', store=True,
        help="Computed patient age at the moment of the evaluation")
    company_id = fields.Many2one('res.company', ondelete='restrict', states=READONLY_STATES,
        string='Hospital', default=lambda self: self.env.user.company_id.id)
    anytime_invoice = fields.Boolean(related="company_id.appointment_anytime_invoice")
    advance_invoice = fields.Boolean(related="company_id.appo_invoice_advance")
    no_invoice = fields.Boolean('Invoice Exempt', states=READONLY_STATES)
    consultation_type = fields.Selection([
        ('consultation','Consultation'),
        ('followup','Follow Up')],'Consultation Type', states=READONLY_STATES)

    diseases_ids = fields.Many2many('hms.diseases', 'diseases_appointment_rel', 'diseas_id', 'appointment_id', 'Diseases', states=READONLY_STATES)
    medical_history = fields.Text(related='patient_id.medical_history', 
        string="Past Medical History", readonly=True)
    patient_diseases_ids = fields.One2many('hms.patient.disease', readonly=True, 
        related='patient_id.patient_diseases_ids', string='Disease History')

    date = fields.Datetime(string='Date', default=fields.Datetime.now, states=READONLY_STATES, tracking=True)
    date_to = fields.Datetime(string='Date To', default=fields.datetime.now() + timedelta(minutes=15), states=READONLY_STATES)
    planned_duration = fields.Float('Duration', default=0.25, states=READONLY_STATES)

    waiting_date_start = fields.Datetime('Waiting Start Date', states=READONLY_STATES)
    waiting_date_end = fields.Datetime('Waiting end Date', states=READONLY_STATES)
    waiting_duration = fields.Float('Wait Time', readonly=True)
    waiting_duration_timer = fields.Float('Wait Timer', readonly=True, default="0.1")

    date_start = fields.Datetime(string='Start Date', states=READONLY_STATES)
    date_end = fields.Datetime(string='End Date', states=READONLY_STATES)
    appointment_duration = fields.Float('Consultation Time', readonly=True)
    appointment_duration_timer = fields.Float('Consultation Timer', readonly=True, default="0.1")

    purpose_id = fields.Many2one('appointment.purpose', ondelete='cascade', 
        string='Purpose', help="Appointment Purpose", states=READONLY_STATES)
    cabin_id = fields.Many2one('appointment.cabin', ondelete='cascade', 
        string='Cabin', help="Appointment Cabin", states=READONLY_STATES)
    treatment_id = fields.Many2one('hms.treatment', ondelete='cascade', 
        string='Treatment', help="Treatment Id", states=READONLY_STATES, tracking=True)

    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Referring Physician', 
        index=True, help='Referring Physician', states=READONLY_STATES)
    responsible_id = fields.Many2one('hms.physician', "Responsible Jr. Doctor", states=READONLY_STATES)
    medical_alert_ids = fields.Many2many('acs.medical.alert', 'appointment_medical_alert_rel','appointment_id', 'alert_id',
        string='Medical Alerts', related='patient_id.medical_alert_ids')
    alert_count = fields.Integer(compute='_get_alert_count', default=0)
    consumable_line_ids = fields.One2many('hms.consumable.line', 'appointment_id',
        string='Consumable Line', states=READONLY_STATES)
    #Only used in case of advance invoice
    consumable_invoice_id = fields.Many2one('account.move', string="Consumables Invoice")

    pause_date_start = fields.Datetime('Pause Start Date', states=READONLY_STATES)
    pause_date_end = fields.Datetime('Pause end Date', states=READONLY_STATES)
    pause_duration = fields.Float('Paused Time', readonly=True)
    prescription_ids = fields.One2many('prescription.order', 'appointment_id', 'Prescriptions')
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', check_company=True, 
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, related invoice will be affected.")
    location = fields.Char(string="Appointment Location", states=READONLY_STATES)
    outside_appointment = fields.Boolean(string="Outside Appointment", states=READONLY_STATES)
    cancel_reason = fields.Text(string="Cancel Reason", states=READONLY_STATES)

    #ACS NOTE: if get error on portal access replace it with compute.
    department_type = fields.Selection(related='department_id.department_type', string="Appointment Department", store=True)

    @api.onchange('department_id')
    def onchange_department(self):
        res = {}
        if self.department_id:
            physicians = self.env['hms.physician'].search([('department_ids', 'in', self.department_id.id)])
            res['domain'] = {'physician_id':[('id','in',physicians.ids)]}
            self.department_type = self.department_id.department_type
        return res

    @api.onchange('date', 'planned_duration')
    def onchange_date_duration(self):
        if self.date:
            if self.planned_duration:
                self.date_to = self.date + timedelta(hours=self.planned_duration)
            else:
                self.date_to = self.date

    @api.onchange('date_to')
    def onchange_date_to(self):
        if self.date and self.date_to:
            diff = self.date_to - self.date
            planned_duration = (diff.days * 24) + (diff.seconds/3600)
            if self.planned_duration != planned_duration:
                self.planned_duration = planned_duration

    @api.model
    def create(self, values):
        if values.get('name', 'New Appointment') == 'New Appointment':
            values['name'] = self.env['ir.sequence'].next_by_code('hms.appointment') or 'New Appointment'
        return super(Appointment, self).create(values)

    def unlink(self):
        for data in self:
            if data.state in ['done']:
                raise UserError(_('You can not delete record in done state'))
        return super(Appointment, self).unlink()

    def print_report(self):
        return self.env.ref('acs_hms.action_appointment_report').report_action(self)

    def action_appointment_send(self):
        '''
        This function opens a window to compose an email, with the template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('acs_hms', 'acs_appointment_email')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'hms.appointment',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def create_invoice(self):
        product_id = self.product_id
        if not product_id:
            raise UserError(_("Please Set Consultation Service first."))
        product_data = [{'product_id': product_id}]
        for consumable in self.consumable_line_ids:
            product_data.append({
                'product_id': consumable.product_id,
                'quantity': consumable.qty,
            })
        inv_data = {
            'ref_physician_id': self.ref_physician_id and self.ref_physician_id.id or False,
            'physician_id': self.physician_id and self.physician_id.id or False,
            'appointment_id': self.id,
            'hospital_invoice_type': 'appointment',
        }

        pricelist_context = {}
        if self.pricelist_id:
            pricelist_context = {'acs_pricelist_id': self.pricelist_id.id}
        invoice = self.with_context(pricelist_context).acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.appointment_done()

        if self.state == 'draft' and not self._context.get('avoid_confirmation'):
            self.appointment_confirm()

    def create_consumed_prod_invoice(self):
        product_data = []
        if not self.consumable_line_ids:
            raise UserError(_("There is no consumed product to invoice."))

        for consumable in self.consumable_line_ids:
            product_data.append({
                'product_id': consumable.product_id,
                'quantity': consumable.qty,
            })
        inv_data = {
            'ref_physician_id': self.ref_physician_id and self.ref_physician_id.id or False,
            'physician_id': self.physician_id and self.physician_id.id or False,
        }

        pricelist_context = {}
        if self.pricelist_id:
            pricelist_context = {'acs_pricelist_id': self.pricelist_id.id}
        invoice = self.with_context(pricelist_context).acs_create_invoice(partner=self.patient_id.partner_id, patient=self.patient_id, product_data=product_data, inv_data=inv_data)
        self.consumable_invoice_id = invoice.id
        if self.state == 'to_invoice':
            self.appointment_done()

    def view_invoice(self):
        appointment_invoices = self.env['account.move'].search([('appointment_id','=',self.id)])
        invoices = self.mapped('invoice_id') + self.mapped('consumable_invoice_id') + appointment_invoices

        action = self.acs_action_view_invoice(invoices)
        action['context'].update({
            'default_partner_id': self.patient_id.partner_id.id,
            'default_patient_id': self.patient_id.id,
        })
        return action

    def action_refer_doctor(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_appointment")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id}
        action['views'] = [(self.env.ref('acs_hms.view_hms_appointment_form').id, 'form')]
        return action

    def action_create_evaluation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.action_acs_patient_evaluation_popup")
        action['domain'] = [('patient_id','=',self.id)]
        action['context'] = {'default_patient_id': self.patient_id.id, 'default_physician_id': self.physician_id.id, 'default_appointment_id': self.id}
        return action

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            self.age = self.patient_id.age
            followup_days = self.env.user.company_id.followup_days
            followup_day_limit = (datetime.now() + timedelta(days=followup_days)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            appointment_id = self.search([('patient_id', '=', self.patient_id.id),('date','<=',followup_day_limit)])
            
            #Avoid setting physician if already there from treatment or manually selected.
            if not self.physician_id:
                self.physician_id = self.patient_id.primary_doctor and self.patient_id.primary_doctor.id
            if appointment_id:
                self.consultation_type = 'followup'
                if self.env.user.company_id.followup_product_id:
                    self.product_id = self.env.user.company_id.followup_product_id.id
            else:
                self.consultation_type = 'consultation'

    @api.onchange('physician_id')
    def onchange_physician(self):
        if self.physician_id:
            if self.physician_id.consultaion_service_id:
                self.product_id = self.physician_id.consultaion_service_id.id

            if self.physician_id.appointment_duration:
                self.planned_duration = self.physician_id.appointment_duration

            if self.consultation_type=='followup':
                if self.physician_id.followup_service_id:
                    self.product_id = self.physician_id.followup_service_id.id

    def appointment_confirm(self):
        if self.company_id.appo_invoice_advance and not self.invoice_id:
            raise UserError(_('Invoice is not created yet'))
        self.state = 'confirm'

    def appointment_waiting(self):
        self.state = 'waiting'
        self.waiting_date_start = datetime.now()
        self.waiting_duration = 0.1

    def appointment_consultation(self):
        if not self.waiting_date_start:
            raise UserError(('No waiting start time defined.'))
        datetime_diff = datetime.now() - self.waiting_date_start
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.waiting_duration = float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102))
        self.state = 'in_consultation'
        self.waiting_date_end = datetime.now()
        self.date_start = datetime.now()

    def action_pause(self):
        self.state = 'pause'
        self.pause_date_start = datetime.now()

        if self.date_start:
            datetime_diff = datetime.now() - self.date_start
            m, s = divmod(datetime_diff.total_seconds(), 60)
            h, m = divmod(m, 60)
            self.appointment_duration = float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102)) - self.pause_duration
        self.date_end = datetime.now()

    def action_start_paused(self):
        self.state = 'in_consultation'
        self.pause_date_end = datetime.now()
        self.date_end = False
        datetime_diff = datetime.now() - self.pause_date_start
        m, s = divmod(datetime_diff.total_seconds(), 60)
        h, m = divmod(m, 60)
        self.pause_duration += float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102))

    def consultation_done(self):
        if self.date_start:
            datetime_diff = datetime.now() - self.date_start
            m, s = divmod(datetime_diff.total_seconds(), 60)
            h, m = divmod(m, 60)
            self.appointment_duration = float(('%0*d')%(2,h) + '.' + ('%0*d')%(2,m*1.677966102)) - self.pause_duration
        self.date_end = datetime.now()
        if (self.no_invoice or self.invoice_id) and not (self.consumable_line_ids and self.advance_invoice and not self.no_invoice and not self.consumable_invoice_id):
            self.appointment_done()
        else:
            self.state = 'to_invoice'
        if self.consumable_line_ids:
            self.consume_appointment_material() 

    def appointment_done(self):
        self.state = 'done'
        self.follow_date = self.date + timedelta(days=self.company_id.sudo().auto_followup_days)

    def appointment_cancel(self):
        self.state = 'cancel'
        self.waiting_date_start = False
        self.waiting_date_end = False

        if self.invoice_id and self.invoice_id.state=='draft':
            self.sudo().invoice_id.unlink()

    def appointment_draft(self):
        self.state = 'draft'

    def action_prescription(self):
        action = self.env["ir.actions.actions"]._for_xml_id("acs_hms.act_open_hms_prescription_order_view")
        action['domain'] = [('appointment_id', '=', self.id)]
        action['context'] = {
                'default_patient_id': self.patient_id.id,
                'default_physician_id': self.physician_id.id,
                'default_diseases_ids': [(6,0,self.diseases_ids.ids)],
                'default_treatment_id': self.treatment_id and self.treatment_id.id or False,
                'default_appointment_id': self.id}
        return action

    def button_pres_req(self):
        action = self.env.ref('acs_hms.act_open_hms_prescription_order_view').read()[0]
        action['domain'] = [('appointment_id', '=', self.id)]
        action['views'] = [(self.env.ref('acs_hms.view_hms_prescription_order_form').id, 'form')]
        action['context'] = {
                'default_patient_id': self.patient_id.id,
                'default_physician_id':self.physician_id.id,
                'default_diseases_ids': [(6,0,self.diseases_ids.ids)],
                'default_treatment_id': self.treatment_id and self.treatment_id.id or False,
                'default_appointment_id': self.id}
        return action
                
    def consume_appointment_material(self):
        for rec in self:
            if not rec.company_id.appointment_usage_location_id:
                raise UserError(_('Please define a appointment location where the consumables will be used.'))
            if not rec.company_id.appointment_stock_location_id:
                raise UserError(_('Please define a appointment location from where the consumables will be taken.'))

            dest_location_id  = rec.company_id.appointment_usage_location_id.id
            source_location_id  = rec.company_id.appointment_stock_location_id.id
            for line in rec.consumable_line_ids.filtered(lambda s: not s.move_id):
                move = self.consume_material(source_location_id, dest_location_id,
                    {
                        'product': line.product_id,
                        'qty': line.qty,
                    })
                move.appointment_id = rec.id
                line.move_id = move.id


class StockMove(models.Model):
    _inherit = "stock.move"

    appointment_id = fields.Many2one('hms.appointment', string="Appointment", ondelete="restrict")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: