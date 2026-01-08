from odoo import models, fields, api

class PoultryCashier(models.Model):
    _name = 'poultry.cashier'
    _description = 'Poultry Cashier'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # enable chatter & activities

    name = fields.Char("Cashier Name", required=True, tracking=True)
    phone = fields.Char("Phone")
    email = fields.Char("Email")

    active = fields.Boolean(default=True)
