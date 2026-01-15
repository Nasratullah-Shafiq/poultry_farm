# # from odoo import models, fields, api
# # from odoo.exceptions import ValidationError
# #
# #
# # class CashDepositReportWizard(models.TransientModel):
# #     _name = 'cash.deposit.report.wizard'
# #     _description = 'Cash Deposit Report Wizard'
# #
# #     start_date = fields.Date(string="Start Date", required=True)
# #     end_date = fields.Date(string="End Date", required=True)
# #
# #     branch_id = fields.Many2one(
# #         'poultry.branch',
# #         string="Branch"
# #     )
# #
# #     cash_account_id = fields.Many2one(
# #         'poultry.cash.account',
# #         string="Cash Account",
# #         domain="[('branch_id', '=', branch_id)]"
# #     )
# #
# #     total_amount = fields.Monetary(
# #         string="Total Deposit",
# #         readonly=True
# #     )
# #
# #     currency_id = fields.Many2one(
# #         'res.currency',
# #         default=lambda self: self.env.company.currency_id,
# #         readonly=True
# #     )
# #
# #     deposit_lines = fields.One2many(
# #         'cash.deposit.report.line',
# #         'wizard_id',
# #         string="Deposit Details",
# #         readonly=True
# #     )
# #
# #     # -----------------------------
# #     # Validations
# #     # -----------------------------
# #     @api.constrains('start_date', 'end_date')
# #     def _check_date_range(self):
# #         for rec in self:
# #             if rec.end_date < rec.start_date:
# #                 raise ValidationError("End Date cannot be earlier than Start Date.")
# #
# #     # -----------------------------
# #     # Domain Builder
# #     # -----------------------------
# #     def _get_domain(self):
# #         self.ensure_one()
# #
# #         domain = [
# #             ('date', '>=', self.start_date),
# #             ('date', '<=', self.end_date),
# #         ]
# #
# #         if self.branch_id:
# #             domain.append(('branch_id', '=', self.branch_id.id))
# #
# #         if self.cash_account_id:
# #             domain.append(('cash_account_id', '=', self.cash_account_id.id))
# #
# #         return domain
# #
# #     # -----------------------------
# #     # Generate Report
# #     # -----------------------------
# #     def generate_report(self):
# #         self.ensure_one()
# #
# #         Deposit = self.env['poultry.cash.deposit']
# #         deposits = Deposit.search(self._get_domain(), order='date asc')
# #
# #         self.deposit_lines.unlink()
# #         total = 0.0
# #
# #         for dep in deposits:
# #             self.env['cash.deposit.report.line'].create({
# #                 'wizard_id': self.id,
# #                 'date': dep.date,
# #                 'branch_id': dep.branch_id.id,
# #                 'cash_account_id': dep.cash_account_id.id,
# #                 'account_type': dep.account_type,
# #                 'amount': dep.amount,
# #                 'user_id': dep.user_id.id,
# #                 'note': dep.note,
# #             })
# #             total += dep.amount
# #
# #         self.total_amount = total
# #
# #         return {
# #             'type': 'ir.actions.act_window',
# #             'res_model': self._name,
# #             'view_mode': 'form',
# #             'res_id': self.id,
# #             'target': 'new',
# #         }
# #
# #     # -----------------------------
# #     # PDF Report
# #     # -----------------------------
# #     def print_pdf_report(self):
# #         self.generate_report()
# #         return self.env.ref(
# #             'poultry_farm.action_cash_deposit_report'
# #         ).report_action(self)
# #
# #
# # class CashDepositReportLine(models.TransientModel):
# #     _name = 'cash.deposit.report.line'
# #     _description = 'Cash Deposit Report Line'
# #
# #     wizard_id = fields.Many2one(
# #         'cash.deposit.report.wizard',
# #         ondelete='cascade'
# #     )
# #
# #     date = fields.Datetime(string="Date")
# #     branch_id = fields.Many2one('poultry.branch', string="Branch")
# #     cash_account_id = fields.Many2one('poultry.cash.account', string="Account No")
# #
# #     account_type = fields.Selection([
# #         ('main', 'Main Account'),
# #         ('marco', 'Marco Account'),
# #         ('bagram', 'Bagram Account'),
# #         ('cashier', 'Cashier Account'),
# #     ], string="Account")
# #
# #     amount = fields.Monetary(string="Amount", currency_field='currency_id')
# #     user_id = fields.Many2one('res.users', string="Deposited By")
# #     note = fields.Text(string="Note")
# #
# #     currency_id = fields.Many2one(
# #         'res.currency',
# #         default=lambda self: self.env.company.currency_id
# #     )
#
#
# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
# class CashDepositReportWizard(models.TransientModel):
#     _name = 'cash.deposit.report.wizard'
#     _description = 'Cash Deposit Report Wizard'
#
#     start_date = fields.Date(string="Start Date", required=True)
#     end_date = fields.Date(string="End Date", required=True)
#
#     branch_id = fields.Many2one(
#         'poultry.branch',
#         string="Branch"
#     )
#
#     cash_account_id = fields.Many2one(
#         'poultry.cash.account',
#         string="Cash Account",
#         domain="[('branch_id', '=', branch_id)]"
#     )
#
#     total_amount = fields.Monetary(
#         string="Total Deposit",
#         readonly=True
#     )
#
#     currency_id = fields.Many2one(
#         'res.currency',
#         default=lambda self: self.env.company.currency_id,
#         readonly=True
#     )
#
#     deposit_lines = fields.One2many(
#         'cash.deposit.report.line',
#         'wizard_id',
#         string="Deposit Details",
#         readonly=True
#     )
#
#     currency_totals = fields.One2many(
#         'cash.deposit.report.currency.line',
#         'wizard_id',
#         string="Totals by Currency",
#         readonly=True
#     )
#
#     # -----------------------------
#     # Validations
#     # -----------------------------
#     @api.constrains('start_date', 'end_date')
#     def _check_date_range(self):
#         for rec in self:
#             if rec.end_date < rec.start_date:
#                 raise ValidationError("End Date cannot be earlier than Start Date.")
#
#     # -----------------------------
#     # Domain Builder
#     # -----------------------------
#     def _get_domain(self):
#         self.ensure_one()
#
#         domain = [
#             ('date', '>=', self.start_date),
#             ('date', '<=', self.end_date),
#         ]
#
#         if self.branch_id:
#             domain.append(('branch_id', '=', self.branch_id.id))
#
#         if self.cash_account_id:
#             domain.append(('cash_account_id', '=', self.cash_account_id.id))
#
#         return domain
#
#     # -----------------------------
#     # Generate Report
#     # -----------------------------
#     # def generate_report(self):
#     #     self.ensure_one()
#     #
#     #     Deposit = self.env['poultry.cash.deposit']
#     #     deposits = Deposit.search(self._get_domain(), order='date asc')
#     #
#     #     # Clear previous lines
#     #     self.deposit_lines.unlink()
#     #     self.currency_totals.unlink()
#     #
#     #     total = 0.0
#     #     currency_dict = {}  # currency_id -> total
#     #
#     #     for dep in deposits:
#     #         currency_id = dep.cash_account_id.currency_type.id if dep.cash_account_id.currency_type else self.env.company.currency_id.id
#     #
#     #         self.env['cash.deposit.report.line'].create({
#     #             'wizard_id': self.id,
#     #             'date': dep.date,
#     #             'branch_id': dep.branch_id.id,
#     #             'cash_account_id': dep.cash_account_id.id,
#     #             'account_type': dep.account_type,
#     #             'amount': dep.amount,
#     #             'user_id': dep.user_id.id,
#     #             'note': dep.note,
#     #             'currency_id': currency_id,
#     #         })
#     #
#     #         total += dep.amount
#     #         currency_dict[currency_id] = currency_dict.get(currency_id, 0.0) + dep.amount
#     #
#     #     self.total_amount = total
#     #
#     #     # Create currency total lines
#     #     for currency_id, amount in currency_dict.items():
#     #         self.env['cash.deposit.report.currency.line'].create({
#     #             'wizard_id': self.id,
#     #             'currency_id': currency_id,
#     #             'total_amount': amount,
#     #         })
#     #
#     #     return {
#     #         'type': 'ir.actions.act_window',
#     #         'res_model': self._name,
#     #         'view_mode': 'form',
#     #         'res_id': self.id,
#     #         'target': 'new',
#     #     }
#
#     def generate_report(self):
#         self.ensure_one()
#
#         Deposit = self.env['poultry.cash.deposit']
#         deposits = Deposit.search(self._get_domain(), order='date asc')
#
#         # Clear previous lines
#         self.deposit_lines.unlink()
#
#         # Initialize currency-wise totals
#         total_afn = 0.0
#         total_usd = 0.0
#         total_kld = 0.0
#
#         for dep in deposits:
#             # Map string to res.currency record
#             currency = None
#             if dep.currency_type == 'afn':
#                 currency = self.env['res.currency'].search([('name', '=', 'AFN')], limit=1)
#             elif dep.currency_type == 'usd':
#                 currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
#             elif dep.currency_type == 'kaldar':
#                 currency = self.env['res.currency'].search([('name', '=', 'KLD')], limit=1)
#
#             # Create deposit line
#             self.env['cash.deposit.report.line'].create({
#                 'wizard_id': self.id,
#                 'date': dep.date,
#                 'branch_id': dep.branch_id.id,
#                 'cash_account_id': dep.cash_account_id.id,
#                 'account_type': dep.account_type,
#                 'amount': dep.amount,
#                 'user_id': dep.user_id.id,
#                 'currency_id': currency.id if currency else False,
#                 'note': dep.note,
#             })
#
#             # Add to totals
#             if dep.currency_type == 'afn':
#                 total_afn += dep.amount
#             elif dep.currency_type == 'usd':
#                 total_usd += dep.amount
#             elif dep.currency_type == 'kaldar':
#                 total_kld += dep.amount
#
#         # Assign totals to wizard fields
#         self.total_afn = total_afn
#         self.total_usd = total_usd
#         self.total_kld = total_kld
#
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': self._name,
#             'view_mode': 'form',
#             'res_id': self.id,
#             'target': 'new',
#         }
#
#     # -----------------------------
#     # PDF Report
#     # -----------------------------
#     def print_pdf_report(self):
#         self.generate_report()
#         return self.env.ref(
#             'poultry_farm.action_cash_deposit_report'
#         ).report_action(self)
#
#
# # -----------------------------
# # Deposit Line Model
# # -----------------------------
# class CashDepositReportLine(models.TransientModel):
#     _name = 'cash.deposit.report.line'
#     _description = 'Cash Deposit Report Line'
#
#     wizard_id = fields.Many2one(
#         'cash.deposit.report.wizard',
#         ondelete='cascade'
#     )
#
#     date = fields.Datetime(string="Date")
#     branch_id = fields.Many2one('poultry.branch', string="Branch")
#     cash_account_id = fields.Many2one('poultry.cash.account', string="Account No")
#
#     account_type = fields.Selection([
#         ('main', 'Main Account'),
#         ('marco', 'Marco Account'),
#         ('bagram', 'Bagram Account'),
#         ('cashier', 'Cashier Account'),
#     ], string="Account")
#
#     amount = fields.Monetary(string="Amount", currency_field='currency_id')
#     user_id = fields.Many2one('res.users', string="Deposited By")
#     note = fields.Text(string="Note")
#
#     currency_id = fields.Many2one(
#         'res.currency',
#         string="Currency",
#         readonly=True
#     )
#
#
# # -----------------------------
# # Currency Summary Line Model
# # -----------------------------
# class CashDepositReportCurrencyLine(models.TransientModel):
#     _name = 'cash.deposit.report.currency.line'
#     _description = 'Cash Deposit Currency Summary Line'
#
#     wizard_id = fields.Many2one(
#         'cash.deposit.report.wizard',
#         ondelete='cascade'
#     )
#     currency_id = fields.Many2one('res.currency', string="Currency")
#     total_amount = fields.Monetary(string="Total Amount", currency_field='currency_id')


from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CashDepositReportWizard(models.TransientModel):
    _name = 'cash.deposit.report.wizard'
    _description = 'Cash Deposit Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    branch_id = fields.Many2one('poultry.branch', string="Branch")
    cash_account_id = fields.Many2one(
        'poultry.cash.account',
        string="Cash Account",
        domain="[('branch_id', '=', branch_id)]"
    )

    # Currency-wise totals
    total_afn = fields.Monetary(
        string="Total Afghani Deposit",
        readonly=True,
        currency_field='currency_afn_id'
    )
    total_usd = fields.Monetary(
        string="Total USD Deposit",
        readonly=True,
        currency_field='currency_usd_id'
    )
    total_kld = fields.Monetary(
        string="Total Kaldar Deposit",
        readonly=True,
        currency_field='currency_kld_id'
    )

    currency_afn_id = fields.Many2one(
        'res.currency',
        string="AFN Currency",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'AFN')], limit=1),
        readonly=True
    )
    currency_usd_id = fields.Many2one(
        'res.currency',
        string="USD Currency",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1),
        readonly=True
    )
    currency_kld_id = fields.Many2one(
        'res.currency',
        string="KLD Currency",
        default=lambda self: self.env['res.currency'].search([('name', '=', 'KLD')], limit=1),
        readonly=True
    )

    deposit_lines = fields.One2many(
        'cash.deposit.report.line',
        'wizard_id',
        string="Deposit Details",
        readonly=True
    )

    # -----------------------------
    # Validations
    # -----------------------------
    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date.")

    # -----------------------------
    # Domain Builder
    # -----------------------------
    def _get_domain(self):
        self.ensure_one()
        domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        if self.cash_account_id:
            domain.append(('cash_account_id', '=', self.cash_account_id.id))
        return domain

    # -----------------------------
    # Generate Report
    # -----------------------------
    def generate_report(self):
        self.ensure_one()
        Deposit = self.env['poultry.cash.deposit'].search(self._get_domain(), order='date asc')

        # Clear previous lines
        self.deposit_lines.unlink()

        # Initialize totals
        total_afn = 0.0
        total_usd = 0.0
        total_kld = 0.0

        for dep in Deposit:
            # Map string currency to actual res.currency record
            currency = None
            if dep.currency_type == 'afn':
                currency = self.currency_afn_id
                total_afn += dep.amount
            elif dep.currency_type == 'usd':
                currency = self.currency_usd_id
                total_usd += dep.amount
            elif dep.currency_type == 'kaldar':
                currency = self.currency_kld_id
                total_kld += dep.amount

            # Create deposit line
            self.env['cash.deposit.report.line'].create({
                'wizard_id': self.id,
                'date': dep.date,
                'branch_id': dep.branch_id.id,
                'cash_account_id': dep.cash_account_id.id,
                'account_type': dep.account_type,
                'amount': dep.amount,
                'user_id': dep.user_id.id,
                'currency_id': currency.id if currency else False,
                'note': dep.note,
            })

        # Assign totals to wizard fields
        self.total_afn = total_afn
        self.total_usd = total_usd
        self.total_kld = total_kld

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    # -----------------------------
    # PDF Report
    # -----------------------------
    def print_pdf_report(self):
        self.generate_report()
        return self.env.ref('poultry_farm.action_cash_deposit_report').report_action(self)


class CashDepositReportLine(models.TransientModel):
    _name = 'cash.deposit.report.line'
    _description = 'Cash Deposit Report Line'

    wizard_id = fields.Many2one('cash.deposit.report.wizard', ondelete='cascade')
    date = fields.Datetime(string="Date")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    cash_account_id = fields.Many2one('poultry.cash.account', string="Account No")
    account_type = fields.Selection([
        ('main', 'Main Account'),
        ('marco', 'Marco Account'),
        ('bagram', 'Bagram Account'),
        ('cashier', 'Cashier Account'),
    ], string="Account")
    amount = fields.Monetary(string="Amount", currency_field='currency_id')
    user_id = fields.Many2one('res.users', string="Deposited By")
    note = fields.Text(string="Note")
    currency_id = fields.Many2one('res.currency', string="Currency")
