# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Physician(models.Model):
    _inherit = 'hms.physician'

    consultaion_service_id = fields.Many2one('product.product', ondelete='restrict', string='Consultation Service')
    followup_service_id = fields.Many2one('product.product', ondelete='restrict', string='Followup Service')
    appointment_duration = fields.Float('Default Consultation Duration', default=0.25)

    is_primary_surgeon = fields.Boolean(string='Primary Surgeon')
    signature = fields.Binary('Signature')
    hr_presence_state = fields.Selection(related='user_id.employee_id.hr_presence_state')
    appointment_ids = fields.One2many("hms.appointment", "physician_id", "Appointments")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: