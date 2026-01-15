# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
#
# class CashAccountReportWizard(models.TransientModel):
#     _name = 'cash.account.report.wizard'
#     _description = 'Cash Account Report Wizard'
#
#     # -----------------------------
#     # Filters
#     # -----------------------------
#     start_date = fields.Date(string="Start Date")
#     end_date = fields.Date(string="End Date")
#     branch_id = fields.Many2one('poultry.branch', string="Branch")
#
#     # -----------------------------
#     # Totals per currency
#     # -----------------------------
#     total_afn = fields.Float(string="Total Afghani Balance", readonly=True)
#     total_usd = fields.Float(string="Total USD Balance", readonly=True)
#     total_kld = fields.Float(string="Total Kaldar Balance", readonly=True)
#
#     # -----------------------------
#     # Cash Account Lines
#     # -----------------------------
#     account_lines = fields.One2many(
#         'cash.account.report.line', 'wizard_id', string="Cash Accounts", readonly=True
#     )
#
#     # -----------------------------
#     # Validation
#     # -----------------------------
#     @api.constrains('start_date', 'end_date')
#     def _check_date_range(self):
#         for rec in self:
#             if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
#                 raise ValidationError("End Date cannot be earlier than Start Date.")
#
#     # -----------------------------
#     # Domain Builder
#     # -----------------------------
#     def _get_domain(self):
#         domain = []
#         if self.branch_id:
#             domain.append(('branch_id', '=', self.branch_id.id))
#         if self.start_date:
#             domain.append(('last_update', '>=', self.start_date))
#         if self.end_date:
#             domain.append(('last_update', '<=', self.end_date))
#         return domain
#
#     # -----------------------------
#     # Generate Report
#     # -----------------------------
#     def generate_report(self):
#         self.ensure_one()
#
#         domain = self._get_domain()
#         accounts = self.env['poultry.cash.account'].search(domain)
#
#         # Clear previous lines
#         self.account_lines.unlink()
#
#         total_afn = 0.0
#         total_usd = 0.0
#         total_kld = 0.0
#
#         for account in accounts:
#             self.env['cash.account.report.line'].create({
#                 'wizard_id': self.id,
#                 'account_no': account.account_no,
#                 'branch_id': account.branch_id.id,
#                 'account_type': account.account_type,
#                 'balance': account.balance,
#                 'currency_type': account.currency_type,
#                 'cashier_id': account.cashier_id.id if account.cashier_id else False,
#                 'last_update': account.last_update,
#             })
#
#             # Sum totals per currency
#             if account.currency_type == 'afn':
#                 total_afn += account.balance
#             elif account.currency_type == 'usd':
#                 total_usd += account.balance
#             elif account.currency_type == 'kaldar':
#                 total_kld += account.balance
#
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
#         return self.env.ref('poultry_farm.action_cash_account_report').report_action(self)
#
#
# class CashAccountReportLine(models.TransientModel):
#     _name = 'cash.account.report.line'
#     _description = 'Cash Account Report Line'
#
#     wizard_id = fields.Many2one('cash.account.report.wizard', ondelete='cascade')
#
#     account_no = fields.Char(string="Account No")
#     branch_id = fields.Many2one('poultry.branch', string="Branch")
#     account_type = fields.Selection([
#         ('main', 'Main Account'),
#         ('marco', 'Marco Account'),
#         ('bagram', 'Bagram Account'),
#         ('cashier', 'Cashier Account'),
#     ], string="Type")
#     balance = fields.Float(string="Balance")
#     currency_type = fields.Selection([
#         ('afn', 'AFN'),
#         ('usd', 'USD'),
#         ('kaldar', 'Kaldar'),
#     ], string="Currency")
#     cashier_id = fields.Many2one('poultry.cashier', string="Cashier")
#     last_update = fields.Datetime(string="Last Update")

#
# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
# class CashAccountReportWizard(models.TransientModel):
#     _name = 'cash.account.report.wizard'
#     _description = 'Cash Account Report Wizard'
#
#     # Select a single account
#     account_id = fields.Many2one(
#         'poultry.cash.account',
#         string="Cash Account",
#         required=True
#     )
#
#     # Totals per currency
#     total_amount = fields.Monetary(
#         string="Total Amount",
#         readonly=True,
#         currency_field='currency_id'
#     )
#
#     currency_id = fields.Many2one(
#         'res.currency',
#         string="Currency",
#         readonly=True
#     )
#
#     # Deposit lines
#     deposit_lines = fields.One2many(
#         'cash.account.report.line',
#         'wizard_id',
#         string="Deposit Details",
#         readonly=True
#     )
#
#     # -----------------------------
#     # Generate Report
#     # -----------------------------
#     def generate_report(self):
#         self.ensure_one()
#
#         if not self.account_id:
#             raise ValidationError("Please select a cash account.")
#
#         # Clear previous lines
#         self.deposit_lines.unlink()
#
#         total_amount = 0.0
#
#         # Loop over deposits of the selected account
#         for dep in self.account_id.deposit_ids:
#             self.env['cash.account.report.line'].create({
#                 'wizard_id': self.id,
#                 'date': dep.date,
#                 'account_type': self.account_id.account_type,
#                 'amount': dep.amount,
#                 'user_id': dep.user_id.id,
#                 'note': dep.note,
#             })
#             total_amount += dep.amount
#
#         self.total_amount = total_amount
#         self.currency_id = self.account_id.currency_type and self.env['res.currency'].search([('name', '=', self.account_id.currency_type.upper())], limit=1)
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
#     # Print PDF
#     # -----------------------------
#     def print_pdf_report(self):
#         self.generate_report()
#         return self.env.ref(
#             'poultry_farm.action_cash_account_report'
#         ).report_action(self)
#
#
# class CashAccountReportLine(models.TransientModel):
#     _name = 'cash.account.report.line'
#     _description = 'Cash Account Report Line'
#
#     wizard_id = fields.Many2one(
#         'cash.account.report.wizard',
#         ondelete='cascade'
#     )
#
#     date = fields.Datetime(string="Date")
#     account_type = fields.Selection([
#         ('main', 'Main Account'),
#         ('marco', 'Marco Account'),
#         ('bagram', 'Bagram Account'),
#         ('cashier', 'Cashier Account'),
#     ], string="Account Type")
#
#     amount = fields.Monetary(string="Amount", currency_field='currency_id')
#     user_id = fields.Many2one('res.users', string="Deposited By")
#     note = fields.Text(string="Note")
#
#     currency_id = fields.Many2one(
#         'res.currency',
#         default=lambda self: self.env.company.currency_id
#     )





from odoo import models, fields, api
from odoo.exceptions import ValidationError

class CashAccountReportWizard(models.TransientModel):
    _name = 'cash.account.report.wizard'
    _description = 'Cash Account Report Wizard'

    # Select account type instead of specific account
    account_type = fields.Selection([
        ('main', 'Main Account'),
        ('marco', 'Marco Account'),
        ('bagram', 'Bagram Account'),
        ('cashier', 'Cashier Account'),
    ], string="Cash Account")

    # Totals per currency
    total_afn = fields.Float(string="Total AFN", readonly=True)
    total_usd = fields.Float(string="Total USD", readonly=True)
    total_kld = fields.Float(string="Total Kaldar", readonly=True)

    # Deposit lines
    deposit_lines = fields.One2many(
        'cash.account.report.line',
        'wizard_id',
        string="Deposit Details",
        readonly=True
    )

    # -----------------------------
    # Generate Report
    # -----------------------------
    def generate_report(self):
        self.ensure_one()

        # Clear previous lines
        self.deposit_lines.unlink()

        total_afn = 0.0
        total_usd = 0.0
        total_kld = 0.0

        # Determine which accounts to include
        domain = []
        if self.account_type:
            domain = [('account_type', '=', self.account_type)]

        accounts = self.env['poultry.cash.account'].search(domain)

        for acc in accounts:
            for dep in acc.deposit_ids:
                self.env['cash.account.report.line'].create({
                    'wizard_id': self.id,
                    'date': dep.date,
                    'account_no': acc.account_no,
                    'account_type': acc.account_type,
                    'currency_type': acc.currency_type,
                    'amount': dep.amount,
                    'user_id': dep.user_id.id,
                    'note': dep.note,
                })
                # Sum totals per currency
                if acc.currency_type == 'afn':
                    total_afn += dep.amount
                elif acc.currency_type == 'usd':
                    total_usd += dep.amount
                elif acc.currency_type == 'kaldar':
                    total_kld += dep.amount

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
    # Print PDF
    # -----------------------------
    def print_pdf_report(self):
        self.generate_report()
        return self.env.ref('poultry_farm.action_cash_account_report').report_action(self)


class CashAccountReportLine(models.TransientModel):
    _name = 'cash.account.report.line'
    _description = 'Cash Account Report Line'

    wizard_id = fields.Many2one('cash.account.report.wizard', ondelete='cascade')
    date = fields.Datetime(string="Date")
    account_no = fields.Char(string="Account No")
    account_type = fields.Selection([
        ('main', 'Main Account'),
        ('marco', 'Marco Account'),
        ('bagram', 'Bagram Account'),
        ('cashier', 'Cashier Account'),
    ], string="Account Type")
    currency_type = fields.Selection([
        ('afn', 'AFN'),
        ('usd', 'USD'),
        ('kaldar', 'Kaldar')
    ], string="Currency")

    amount = fields.Float(string="Amount")
    user_id = fields.Many2one('res.users', string="Deposited By")
    note = fields.Text(string="Note")
