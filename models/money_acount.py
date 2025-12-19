from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import datetime




class PoultryMoneyAccount(models.Model):
    _name = 'poultry.money.account'
    _description = 'Money Account'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)

    # account_type = fields.Selection([
    #     ('branch', 'Branch'),
    #     ('cashier', 'Cashier'),
    # ], required=True)
    account_type = fields.Selection([
        ('main', 'Main'),
        ('marco', 'Marco'),
        ('bagram', 'Bagram'),
        ('cashier', 'Cashier'),
    ], string="Account Type", required=True)

    branch_id = fields.Many2one('poultry.branch')
    cashier_id = fields.Many2one('poultry.cashier')

    currency_type = fields.Selection([
        ('usd', 'USD'),
        ('kaldar', 'Kaldar'),
        ('afn', 'AFN')
    ], required=True, default='afn')

    balance = fields.Float(digits=(16, 2), tracking=True)

    # ✅ CONSTRAINT GOES HERE
    @api.constrains('account_type', 'branch_id', 'cashier_id')
    def _check_account_owner(self):
        for rec in self:
            if rec.account_type == 'branch':
                if not rec.branch_id or rec.cashier_id:
                    raise ValidationError(
                        "Branch account must have a branch and no cashier."
                    )

            if rec.account_type == 'cashier':
                if not rec.cashier_id or rec.branch_id:
                    raise ValidationError(
                        "Cashier account must have a cashier and no branch."
                    )
