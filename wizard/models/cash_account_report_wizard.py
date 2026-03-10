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
