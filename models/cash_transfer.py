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

    def action_confirm(self):
        CashAccount = self.env['poultry.cash.account']

        for rec in self:
            if rec.state == 'confirmed':
                continue

            if rec.amount <= 0:
                raise ValidationError("Transfer amount must be greater than zero.")

            source = rec.from_account_id

            # 🔴 Balance check
            if source.balance < rec.amount:
                raise ValidationError("Insufficient balance in source account.")

            # 🔎 Find destination account by BRANCH + CURRENCY
            dest = CashAccount.search([
                ('branch_id', '=', rec.to_branch_id.id),
                ('currency_type', '=', source.currency_type)
            ], limit=1)

            # 🆕 Create if missing (safe due to SQL constraint)
            if not dest:
                dest = CashAccount.create({
                    'name': f"{rec.to_branch_id.name} - {source.currency_type.upper()}",
                    'branch_id': rec.to_branch_id.id,
                    'currency_type': source.currency_type,
                    'balance': 0.0,
                })

            # 🔐 Lock rows (prevents race conditions)
            source = source.with_for_update()
            dest = dest.with_for_update()

            # ➖ Deduct from source
            source.write({
                'balance': source.balance - rec.amount
            })

            # ➕ Add to destination
            dest.write({
                'balance': dest.balance + rec.amount
            })

            rec.state = 'confirmed'

    # def action_confirm(self):
    #     for rec in self:
    #         if rec.state == 'confirmed':
    #             continue
    #
    #         if rec.from_account_id == rec.to_account_id:
    #             raise ValidationError("Cannot transfer to the same account.")
    #
    #         if rec.amount <= 0:
    #             raise ValidationError("Transfer amount must be greater than zero.")
    #
    #         # Check if source account has enough balance
    #         if rec.from_account_id.balance < rec.amount:
    #             raise ValidationError("Insufficient balance in source account.")
    #
    #         # ✅ Deduct from source account
    #         rec.from_account_id.write({
    #             'balance': rec.from_account_id.balance - rec.amount
    #         })
    #
    #         # ✅ Add to destination account
    #         rec.to_account_id.write({
    #             'balance': rec.to_account_id.balance + rec.amount
    #         })
    #
    #         # Update state
    #         rec.state = 'confirmed'

