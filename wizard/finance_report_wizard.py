from odoo import models, fields, api


class PoultryFinanceReport(models.TransientModel):
    _name = 'poultry.finance.report'
    _description = 'Comprehensive Poultry Finance Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")

    total_income = fields.Monetary(string="Total Income", readonly=True)
    total_sales = fields.Monetary(string="Total Sales", readonly=True)
    total_purchases = fields.Monetary(string="Total Purchases", readonly=True)
    total_expenses = fields.Monetary(string="Total Expenses", readonly=True)
    total_salaries = fields.Monetary(string="Total Salaries", readonly=True)
    total_feed = fields.Monetary(string="Total Feed Cost", readonly=True)
    total_medicine = fields.Monetary(string="Total Medicine Cost", readonly=True)
    total_vaccination = fields.Monetary(string="Total Vaccination Cost", readonly=True)
    net_profit = fields.Monetary(string="Net Profit", readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # -------------------------------------------------------------------
    # Step 1: Calculate all totals
    # -------------------------------------------------------------------
    def generate_report(self):
        branch_domain = []
        if self.branch_id:
            branch_domain = [('branch_id', '=', self.branch_id.id)]

        date_domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]

        # ---------- Income ----------
        income_entries = self.env['poultry.finance'].search(date_domain + branch_domain + [('entry_type', '=', 'income')])
        self.total_income = sum(income_entries.mapped('amount'))

        # ---------- Sales ----------
        sales_entries = self.env['poultry.sale'].search(date_domain + branch_domain)
        self.total_sales = sum(sales_entries.mapped('revenue'))

        # ---------- Purchases ----------
        purchase_entries = self.env['poultry.purchase'].search(date_domain + branch_domain)
        self.total_purchases = sum(purchase_entries.mapped('total'))

        # ---------- Expenses ----------
        expense_entries = self.env['poultry.finance'].search(date_domain + branch_domain + [('entry_type', '=', 'expense')])
        self.total_expenses = sum(expense_entries.mapped('amount'))

        # ---------- Salaries ----------
        salary_entries = self.env['poultry.salary'].search([
            ('payment_date', '>=', self.start_date),
            ('payment_date', '<=', self.end_date)
        ])
        if self.branch_id:
            salary_entries = salary_entries.filtered(lambda r: r.employee_id.branch_id == self.branch_id)
        self.total_salaries = sum(salary_entries.mapped('amount'))

        # ---------- Feed Cost ----------
        feed_entries = self.env['poultry.feed'].search(date_domain + branch_domain)
        self.total_feed = sum([f.quantity * (f.purchase_price or 0.0) for f in feed_entries])

        # ---------- Medicine Cost ----------
        medicine_entries = self.env['poultry.medicine'].search(date_domain + branch_domain)
        self.total_medicine = sum([m.quantity * (m.purchase_price or 0.0) for m in medicine_entries])

        # ---------- Vaccination Cost ----------
        vaccination_cost_entries = self.env['poultry.finance'].search(
            date_domain + branch_domain + [('description', 'ilike', 'Vaccination')]
        )
        self.total_vaccination = sum(vaccination_cost_entries.mapped('amount'))

        # ---------- Net Profit ----------
        self.net_profit = (
            self.total_income + self.total_sales
            - (self.total_purchases + self.total_expenses + self.total_salaries + self.total_feed + self.total_medicine + self.total_vaccination)
        )

    def compute_report(self):
        self.generate_report()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',  # keep it as popup
        }

    @api.onchange('start_date', 'end_date', 'branch_id')
    def _onchange_generate_report(self):
        self.generate_report()

    # -------------------------------------------------------------------
    # Step 2: Print PDF report
    # -------------------------------------------------------------------
    def print_pdf_report(self):
        """Generate the PDF finance report"""
        return self.env.ref('poultry_farm.action_poultry_finance_report').report_action(self)
