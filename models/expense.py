from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import datetime

class PoultryExpense(models.Model):
    _name = 'poultry.expense'
    _description = 'Branch Expense'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Expense Description", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch", required=True)
    cash_account_id = fields.Many2one('poultry.cash.account', string="Cash Account", required=True, readonly=True)
    cash_balance = fields.Float(
        string="Current Cash Balance",
        related='cash_account_id.balance',
        readonly=True,
        store=False  # you can set store=True if you want it stored in DB
    )
    expense_type_id = fields.Many2one('poultry.expense.type', string="Expense Type", required=True)
    amount = fields.Float(string="Amount", required=True)
    date = fields.Date(default=fields.Date.today)
    user_id = fields.Many2one('res.users', string="Recorded By", default=lambda self: self.env.user)
    note = fields.Text(string="Note")

    # Computed month and year for search panel
    expense_month = fields.Selection(
        [
            ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
            ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        string="Month",
        compute="_compute_year_month",
        store=True
    )

    expense_year = fields.Selection(
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
                raise ValidationError("Expense amount must be greater than 0!")

    # Compute month and year from date
    @api.depends('date')
    def _compute_year_month(self):
        for rec in self:
            if rec.date:
                rec.expense_month = str(rec.date.month)
                rec.expense_year = str(rec.date.year)
            else:
                rec.expense_month = False
                rec.expense_year = False

    # Selection method for years
    def _get_year_selection(self):
        current_year = datetime.date.today().year
        return [(str(y), str(y)) for y in range(current_year - 10, current_year + 1)]

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Expense amount must be greater than zero!")

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            account = self.env['poultry.cash.account'].search([('branch_id', '=', self.branch_id.id)], limit=1)
            if account:
                self.cash_account_id = account.id

    @api.model
    def create(self, vals):
        """Override create to deduct expense amount from the branch cash account."""
        if 'branch_id' in vals and not vals.get('cash_account_id'):
            account = self.env['poultry.cash.account'].search([('branch_id', '=', vals['branch_id'])], limit=1)
            if account:
                vals['cash_account_id'] = account.id
            else:
                raise UserError("No cash account found for the selected branch!")

        record = super().create(vals)

        # ---------------- Update Cash Account ----------------
        cash_account = record.cash_account_id
        if record.amount > cash_account.balance:
            raise UserError(
                f"Not enough cash in this branch account!\n"
                f"Available: {cash_account.balance}, Requested: {record.amount}"
            )

        return record






class PoultryExpenseType(models.Model):
    _name = "poultry.expense.type"
    _description = "Expense Type"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Expense Type", required=True, tracking=True)


    _sql_constraints = [
        ("unique_name", "unique(name)", "Expense Type name must be unique!")
    ]