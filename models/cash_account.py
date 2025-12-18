from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import datetime

class PoultryCashAccount(models.Model):
    _name = "poultry.cash.account"
    _description = "Branch Cash Account"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Account Name",  readonly=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch", required=True)
    balance = fields.Float(string="Cash Balance",tracking=True)
    # usd_balance = fields.Float("USD Balance", digits=(16, 2), tracking=True)
    # kaldar_balance = fields.Float("Kaldar Balance", digits=(16, 2), tracking=True)
    # afn_balance = fields.Float("AFN Balance", digits=(16, 2), tracking=True)

    last_update = fields.Datetime(string="Last Updated", default=fields.Datetime.now)
    currency_type = fields.Selection([
        ('usd', 'USD'),
        ('kaldar', 'Kaldar'),
        ('afn', 'AFN')
    ], string="Currency", required=True)

    # _sql_constraints = [
    #     ('unique_branch', 'unique(branch_id)', "Each branch can only have one cash account!")
    # ]
    deposit_ids = fields.One2many('poultry.cash.deposit', 'cash_account_id', string="Deposits")
    expense_ids = fields.One2many('poultry.expense', 'cash_account_id', string='Expenses')

    @api.model
    def create(self, vals):
        if 'branch_id' in vals:
            branch = self.env['poultry.branch'].browse(vals['branch_id'])
            # Take first 3 letters of branch name, uppercase
            code = (branch.name[:3] or 'XXX').upper()
            vals['name'] = f"{code}001"  # 001 because only one account per branch
        return super().create(vals)




class PoultryCashDeposit(models.Model):
    _name = "poultry.cash.deposit"
    _description = "Cash Deposit to Branch Account"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cash_account_id = fields.Many2one('poultry.cash.account', string="Cash Account", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch", related='cash_account_id.branch_id', readonly=True, store=True)
    amount = fields.Float(string="Deposit Amount", required=True)
    date = fields.Datetime(string="Deposit Date", default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="Deposited By", default=lambda self: self.env.user)
    currency_type = fields.Selection([
        ('usd', 'USD'),
        ('kaldar', 'Kaldar'),
        ('afn', 'AFN')
    ], string="Currency", required=True)
    note = fields.Text(string="Note")

    # Computed month and year for search panel
    deposit_month = fields.Selection(
        [
            ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
            ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        string="Month",
        compute="_compute_year_month",
        store=True
    )

    deposit_year = fields.Selection(
        selection="_get_year_selection",
        string="Year",
        compute="_compute_year_month",
        store=True
    )

    # Prevent saving zero or negative amounts
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError("Deposit amount must be greater than 0!")

    # Compute month and year from date
    @api.depends('date')
    def _compute_year_month(self):
        for rec in self:
            if rec.date:
                rec.deposit_month = str(rec.date.month)
                rec.deposit_year = str(rec.date.year)
            else:
                rec.deposit_month = False
                rec.deposit_year = False

    # Selection method for years
    def _get_year_selection(self):
        current_year = datetime.date.today().year
        return [(str(y), str(y)) for y in range(current_year - 10, current_year + 1)]

 # ✅ ADD AMOUNT TO CASH ACCOUNT BALANCE
    def action_confirm(self):
        CashAccount = self.env['poultry.cash.account']

        for rec in self:
            if rec.state == 'confirmed':
                continue

            if rec.amount <= 0:
                raise ValidationError("Deposit amount must be greater than zero.")

            # 🔎 Find account by BRANCH + CURRENCY
            account = CashAccount.search([
                ('branch_id', '=', rec.branch_id.id),
                ('currency_type', '=', rec.currency_type)
            ], limit=1)

            # 🆕 Create if not found
            if not account:
                account = CashAccount.create({
                    'name': f"{rec.branch_id.name} - {rec.currency_type.upper()}",
                    'branch_id': rec.branch_id.id,
                    'currency_type': rec.currency_type,
                    'balance': 0.0,
                })

            # 🔐 Lock record to avoid race conditions
            account = account.with_for_update()

            # ➕ Add amount
            account.write({
                'balance': account.balance + rec.amount,
                'last_update': fields.Datetime.now(),
            })

            # 🔗 Link deposit to account (audit)
            rec.cash_account_id = account.id
            rec.state = 'confirmed'
