from odoo import models, fields

class PoultryCashier(models.Model):
    _name = 'poultry.cashier'
    _description = 'Poultry Cashier'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # enable chatter & activities

    name = fields.Char("Cashier Name", required=True, tracking=True)
    phone = fields.Char("Phone")
    email = fields.Char("Email")

    usd_balance = fields.Float("USD Balance", default=0, digits=(16,2), tracking=True)
    kaldar_balance = fields.Float("Kaldar Balance", default=0, digits=(16,2), tracking=True)
    afn_balance = fields.Float("AFN Balance", default=0, digits=(16,2), tracking=True)

    active = fields.Boolean(default=True)
