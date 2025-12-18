from odoo import models, fields, api

class PoultryCashier(models.Model):
    _name = 'poultry.cashier'
    _description = 'Poultry Cashier'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # enable chatter & activities

    name = fields.Char("Cashier Name", required=True, tracking=True)
    phone = fields.Char("Phone")
    email = fields.Char("Email")
    amount_balance = fields.Float("USD Balance", default=0, digits=(16,2), tracking=True)
    currency_type = fields.Selection([
        ('usd', 'USD'),
        ('kaldar', 'Kaldar'),
        ('afn', 'AFN')
    ], string="Currency", required=True)

    usd_balance = fields.Float("USD Balance", default=0, digits=(16,2), tracking=True)
    kaldar_balance = fields.Float("Kaldar Balance", default=0, digits=(16,2), tracking=True)
    afn_balance = fields.Float("AFN Balance", default=0, digits=(16,2), tracking=True)

    active = fields.Boolean(default=True)

    @api.model
    def action_reconcile_cash(self):
        # Example logic for reconciliation
        for rec in self:
            # you can put reconciliation logic here
            # for now we just log a message
            rec.message_post(body="Reconciliation done")

    @api.model
    def action_reset_balances(self):
        for rec in self:
            rec.usd_balance = 0
            rec.kaldar_balance = 0
            rec.afn_balance = 0
            rec.message_post(body="Balances reset to 0")
