from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import datetime


class PoultryCashTransfer(models.Model):
    _name = 'poultry.cash.transfer'
    _description = 'Cash Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('poultry.cash.transfer'), readonly=True)

    from_account_id = fields.Many2one('poultry.cash.account', string="From Account")
    from_currency_type = fields.Selection(related='from_account_id.currency_type', store=True)

    from_branch_id = fields.Many2one('poultry.branch', string="Branch", related='from_account_id.branch_id', store=True)
    from_cashier_id = fields.Many2one('poultry.cashier', string="From Cashier")

    from_account_balance = fields.Float(string="Account Balance", related='from_account_id.balance', readonly=True, store=True)
    from_account_type = fields.Selection([
        ('main', 'Main'),
        ('marco', 'Marco'),
        ('bagram', 'Bagram'),
        ('cashier', 'Cashier'),
    ], string="Account Type", required=True)




    to_account_type = fields.Selection([
        ('main', 'Main'),
        ('marco', 'Marco'),
        ('bagram', 'Bagram'),
        ('cashier', 'Cashier'),
    ], string="Account Type", required=True)

    to_account_id = fields.Many2one(
        'poultry.cash.account',
        string="To Account"
    )
    to_currency_type = fields.Selection(
        related='to_account_id.currency_type',
        store=True,
        readonly=True
    )

    to_branch_id = fields.Many2one('poultry.branch', string="Branch", related='to_account_id.branch_id', store=True)
    to_cashier_id = fields.Many2one('poultry.cashier', string="To Cashier")
    to_account_balance = fields.Float(
        string="Account Balance",
        related='to_account_id.balance',
        readonly=True,
        store=True
    )

    amount = fields.Float(required=True)
    date = fields.Date(default=fields.Date.today)
    note = fields.Text()

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed')],
        default='draft',
        tracking=True
    )


    @api.constrains('from_account_id', 'to_account_id')
    def _check_accounts(self):
        for rec in self:
            if rec.from_account_id == rec.to_account_id:
                raise ValidationError("Source and destination accounts must be different.")

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Amount must be greater than zero.")

    @api.constrains('from_account_id', 'to_account_id', 'amount')
    def _check_transfer_rules(self):
        for rec in self:
            if not rec.from_account_id or not rec.to_account_id:
                continue

            # ❌ Same account
            if rec.from_account_id.id == rec.to_account_id.id:
                raise ValidationError(
                    "You cannot transfer cash to the same account."
                )

            # ❌ Different currency
            if rec.from_currency_type != rec.to_currency_type:
                raise ValidationError(
                    "Currency mismatch. Source and destination accounts must have the same currency."
                )

            # ❌ Invalid amount
            if rec.amount <= 0:
                raise ValidationError(
                    "Transfer amount must be greater than zero."
                )

            # ❌ Insufficient balance
            if rec.from_account_id.balance < rec.amount:
                raise ValidationError(
                    "Insufficient balance in the source account."
                )

    def action_confirm(self):
        for rec in self:
            if rec.state == 'confirmed':
                continue

            from_account = rec.from_account_id
            to_account = rec.to_account_id

            # Double safety (important)
            if from_account.balance < rec.amount:
                raise ValidationError(
                    "Insufficient balance in the source account."
                )

            # 🔄 Balance update
            from_account.balance -= rec.amount
            to_account.balance += rec.amount

            from_account.last_update = fields.Datetime.now()
            to_account.last_update = fields.Datetime.now()

            rec.state = 'confirmed'

