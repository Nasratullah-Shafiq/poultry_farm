from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import datetime


class PoultryCashTransfer(models.Model):
    _name = 'poultry.cash.transfer'
    _description = 'Cash Transfer'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(default=lambda self: self.env['ir.sequence'].next_by_code('poultry.cash.transfer'), readonly=True)

    from_account_id = fields.Many2one(
        'poultry.cash.account',
        string="From Account",
        required=True
    )
    from_branch_id = fields.Many2one('poultry.branch', string="Branch", related='from_account_id.branch_id', readonly=True,
                                store=True)

    from_account_balance = fields.Float(string="Account Balance", related='from_account_id.balance', readonly=True, store=True)

    to_account_id = fields.Many2one(
        'poultry.cash.account',
        string="To Account",
        required=True
    )
    to_branch_id = fields.Many2one('poultry.branch', string="Branch", related='to_account_id.branch_id', readonly=True,
                                store=True)
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

    # def action_confirm(self):
    #     for rec in self:
    #         if rec.from_account_id.balance < rec.amount:
    #             raise ValidationError("Insufficient balance in Main Account.")
    #
    #         # Deduct from main account
    #         rec.from_account_id.balance -= rec.amount
    #
    #         # Add to destination account
    #         rec.to_account_id.balance += rec.amount
    #
    #         rec.state = 'confirmed'

    def action_confirm(self):
        for rec in self:
            if rec.from_account_id == rec.to_account_id:
                raise ValidationError("Cannot transfer to the same account!")

            # Check sufficient balance in the source account
            if rec.amount > rec.from_account_id.balance:
                raise ValidationError(f"Insufficient balance in account {rec.from_account_id.name}!")

            # Deduct from source account's balance (write to main model)
            rec.from_account_id.write({'balance': rec.from_account_id.balance - rec.amount})

            # Add to destination account's balance (write to main model)
            rec.to_account_id.write({'balance': rec.to_account_id.balance + rec.amount})

            # Mark this transfer as confirmed
            rec.state = 'confirmed'

