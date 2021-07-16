# -*- coding: utf-8 -*-
# Part of AlmightyCS See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    patient_registration_product_id = fields.Many2one('product.product', 
        related='company_id.patient_registration_product_id',
        domain=[('type','=','service')],
        string='Patient Registration Invoice Product', 
        ondelete='cascade', help='Registration Product', readonly=False)
    treatment_registration_product_id = fields.Many2one('product.product', 
        related='company_id.treatment_registration_product_id',
        domain=[('type','=','service')],
        string='Treatment Registration Invoice Product', 
        ondelete='cascade', help='Registration Product', readonly=False)
    consultation_product_id = fields.Many2one('product.product', 
        related='company_id.consultation_product_id',
        domain=[('type','=','service')],
        string='Consultation Invoice Product', 
        ondelete='cascade', help='Consultation Product', readonly=False)
    followup_days = fields.Float(related='company_id.followup_days', string='Followup Days', readonly=False)
    followup_product_id = fields.Many2one('product.product', 
        related='company_id.followup_product_id',
        domain=[('type','=','service')],
        string='Follow-up Invoice Product', 
        ondelete='cascade', help='Followup Product', readonly=False)
    registration_date = fields.Char(related='company_id.registration_date', string='Date of Registration', readonly=False)
    appointment_anytime_invoice = fields.Boolean(related='company_id.appointment_anytime_invoice', string="Allow Invoice Anytime in Appointment", readonly=False)
    appo_invoice_advance = fields.Boolean(related='company_id.appo_invoice_advance', string="Invoice before Confirmation in Appointment", readonly=False)
    appointment_usage_location_id = fields.Many2one('stock.location', 
        related='company_id.appointment_usage_location_id',
        domain=[('usage','=','customer')],
        string='Usage Location for Consumed Products in Appointment', readonly=False)
    appointment_stock_location_id = fields.Many2one('stock.location', 
        related='company_id.appointment_stock_location_id',
        domain=[('usage','=','internal')],
        string='Stock Location for Consumed Products in Appointment', readonly=False)
    group_patient_registartion_invoicing = fields.Boolean("Patient Registration Invoicing", implied_group='acs_hms.group_patient_registartion_invoicing')
    group_treatment_invoicing = fields.Boolean("Treatment Invoicing", implied_group='acs_hms.group_treatment_invoicing')
    acs_prescription_qrcode = fields.Boolean(related='company_id.acs_prescription_qrcode', string="Print Authetication QrCode on Presctiprion", readonly=False)
    auto_followup_days = fields.Float(related='company_id.auto_followup_days', string='Default Followup on (Days)', readonly=False)

    @api.onchange('appointment_anytime_invoice')
    def onchange_appointment_anytime_invoice(self):
        if self.appointment_anytime_invoice:
            self.appo_invoice_advance = False

    @api.onchange('appo_invoice_advance')
    def onchange_appo_invoice_advance(self):
        if self.appo_invoice_advance:
            self.appointment_anytime_invoice = False
