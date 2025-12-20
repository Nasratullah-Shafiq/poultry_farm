from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime, timedelta
import datetime

class PoultryCashAccount(models.Model):
    _name = "poultry.cash.account"
    _description = "Branch Cash Account"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Account Name",  readonly=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    balance = fields.Float(string="Cash Balance",tracking=True)
    account_type = fields.Selection([
        ('main', 'Main'),
        ('marco', 'Marco'),
        ('bagram', 'Bagram'),
        ('cashier', 'Cashier'),
    ], string="Account Type", required=True)


    cashier_id = fields.Many2one('poultry.cashier')

    last_update = fields.Datetime(string="Last Updated", default=fields.Datetime.now)
    currency_type = fields.Selection([
        ('usd', 'USD'),
        ('kaldar', 'Kaldar'),
        ('afn', 'AFN')
    ], string="Currency", required=True, default='afn')

    # _sql_constraints = [
    #     ('unique_branch', 'unique(branch_id)', "Each branch can only have one cash account!")
    # ]
    deposit_ids = fields.One2many('poultry.cash.deposit', 'cash_account_id', string="Deposits")
    expense_ids = fields.One2many('poultry.expense', 'cash_account_id', string='Expenses')

    @api.constrains('account_type', 'branch_id', 'cashier_id', 'currency_type')
    def _check_unique_currency_account(self):
        for rec in self:
            # Branch accounts
            if rec.account_type != 'cashier':
                if not rec.branch_id:
                    raise ValidationError("Branch account must have a branch.")

                domain = [
                    ('id', '!=', rec.id),
                    ('branch_id', '=', rec.branch_id.id),
                    ('currency_type', '=', rec.currency_type),
                    ('account_type', '!=', 'cashier'),
                ]

                if self.search_count(domain):
                    raise ValidationError(
                        f"Branch '{rec.branch_id.name}' already has a "
                        f"{rec.currency_type.upper()} account."
                    )

            # Cashier accounts
            if rec.account_type == 'cashier':
                if not rec.cashier_id:
                    raise ValidationError("Cashier account must have a cashier.")

                domain = [
                    ('id', '!=', rec.id),
                    ('cashier_id', '=', rec.cashier_id.id),
                    ('currency_type', '=', rec.currency_type),
                    ('account_type', '=', 'cashier'),
                ]

                if self.search_count(domain):
                    raise ValidationError(
                        f"Cashier '{rec.cashier_id.name}' already has a "
                        f"{rec.currency_type.upper()} account."
                    )

    #
    #     return super().create(vals)
    @api.model
    def create(self, vals):

        # =========================
        # BRANCH ACCOUNTS
        # =========================
        if (
                vals.get('account_type') in ('main', 'marco', 'bagram')
                and vals.get('branch_id')
                and vals.get('currency_type')
        ):
            branch = self.env['poultry.branch'].browse(vals['branch_id'])

            # Safety check
            if not branch:
                raise ValidationError("Invalid branch selected.")

            # 1. Branch code
            branch_code = (branch.name or 'XXX')[:3].upper()

            # 2. Currency order
            currency_order = {
                'usd': 1,
                'kaldar': 2,
                'afn': 3,
            }[vals['currency_type']]

            # 3. Branch index (1, 2, 3 ...)
            branch_index = (
                                   self.search_count([
                                       ('branch_id', '=', branch.id),
                                       ('account_type', 'in', ('main', 'marco', 'bagram')),
                                   ]) // 3
                           ) + 1

            # 4. Multiplier (1, 10, 100 ...)
            multiplier = 10 ** (branch_index - 1)

            # 5. Final number
            number = currency_order * multiplier
            number_str = str(number).zfill(3)

            # 6. Currency code
            currency_code = 'KLD' if vals['currency_type'] == 'kaldar' else vals['currency_type'].upper()

            # 7. Final name
            vals['name'] = f"{branch_code}{number_str}{currency_code}"

        # =========================
        # CASHIER ACCOUNTS
        # =========================
        elif (
                vals.get('account_type') == 'cashier'
                and vals.get('cashier_id')
                and vals.get('currency_type')
        ):
            cashier = self.env['poultry.cashier'].browse(vals['cashier_id'])

            if not cashier:
                raise ValidationError("Invalid cashier selected.")

            # 1. Cashier code (first 3 letters)
            cashier_code = (cashier.name or 'XXX')[:3].upper()

            # 2. Currency order
            currency_order = {
                'usd': 1,
                'kaldar': 2,
                'afn': 3,
            }[vals['currency_type']]

            # 3. Cashier index
            cashier_index = (
                                    self.search_count([
                                        ('cashier_id', '=', cashier.id),
                                        ('account_type', '=', 'cashier'),
                                    ]) // 3
                            ) + 1

            # 4. Multiplier
            multiplier = 10 ** (cashier_index - 1)

            # 5. Final number
            number = currency_order * multiplier
            number_str = str(number).zfill(3)

            # 6. Currency code
            currency_code = 'KLD' if vals['currency_type'] == 'kaldar' else vals['currency_type'].upper()

            # 7. Final name
            vals['name'] = f"{cashier_code}{number_str}{currency_code}"

        return super().create(vals)











class PoultryCashDeposit(models.Model):
    _name = "poultry.cash.deposit"
    _description = "Cash Deposit to Branch Account"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cash_account_id = fields.Many2one('poultry.cash.account', string="Cash Account")
    branch_id = fields.Many2one('poultry.branch', string="Branch", related='cash_account_id.branch_id', readonly=True, store=True)
    amount = fields.Float(string="Deposit Amount", required=True)
    date = fields.Datetime(string="Deposit Date", default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="Deposited By", default=lambda self: self.env.user)

    cashier_id = fields.Many2one('poultry.cashier', string="From Cashier")
    account_type = fields.Selection([
        ('main', 'Main'),
        ('marco', 'Marco'),
        ('bagram', 'Bagram'),
        ('cashier', 'Cashier'),
    ], string="Account Type", required=True)
    currency_type = fields.Selection(
        related='cash_account_id.currency_type',
        store=True,
        readonly=True
    )

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

    @api.model
    def create(self, vals):
        record = super().create(vals)

        account = record.cash_account_id
        if not account:
            raise ValidationError(
                "No Cash Account found for the selected Account Type."
            )

        account.balance += record.amount
        account.last_update = fields.Datetime.now()

        return record

    @api.constrains('account_type', 'cash_account_id', 'amount')
    def _validate_account_and_amount(self):
        for rec in self:
            if not rec.cash_account_id:
                raise ValidationError(
                    "No Cash Account exists for the selected Account Type."
                )

            if rec.cash_account_id.account_type != rec.account_type:
                raise ValidationError(
                    "Cash Account does not match the selected Account Type."
                )

            if rec.amount <= 0:
                raise ValidationError(
                    "Deposit amount must be greater than zero."
                )


    @api.onchange('account_type')
    def _onchange_account_type(self):
        if not self.account_type:
            self.cash_account_id = False
            return

        account = self.env['poultry.cash.account'].search(
            [('account_type', '=', self.account_type)],
            limit=1
        )

        if not account:
            self.cash_account_id = False
            return

        self.cash_account_id = account.id
