# from odoo import models, fields, api
# from odoo.exceptions import UserError
# from dateutil.relativedelta import relativedelta
#
#
# class PoultryFinanceReport(models.TransientModel):
#     _name = 'poultry.finance.report'
#     _description = 'Comprehensive Poultry Finance Report Wizard'
#
#     start_date = fields.Date(string="Start Date", required=True)
#     end_date = fields.Date(string="End Date", required=True)
#     branch_id = fields.Many2one('poultry.branch', string="Branch")
#
#     total_income = fields.Monetary(string="Total Income", readonly=True)
#     total_sales = fields.Monetary(string="Total Sales", readonly=True)
#     total_purchases = fields.Monetary(string="Total Purchases", readonly=True)
#     total_expenses = fields.Monetary(string="Total Expenses", readonly=True)
#     total_salaries = fields.Monetary(string="Total Salaries", readonly=True)
#     total_feed = fields.Monetary(string="Total Feed Cost", readonly=True)
#     total_medicine = fields.Monetary(string="Total Medicine Cost", readonly=True)
#     total_vaccination = fields.Monetary(string="Total Vaccination Cost", readonly=True)
#     net_profit = fields.Monetary(string="Net Profit", readonly=True)
#     currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
#
#     # -------------------------------------------------------------------
#     # Step 1: Calculate all totals
#     # -------------------------------------------------------------------
#     def generate_report(self):
#         branch_domain = []
#         if self.branch_id:
#             branch_domain = [('branch_id', '=', self.branch_id.id)]
#
#         date_domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]
#
#         # ---------- Income ----------
#         income_entries = self.env['poultry.finance'].search(
#             date_domain + branch_domain + [('entry_type', '=', 'income')])
#         self.total_income = sum(income_entries.mapped('amount'))
#
#         # ---------- Sales ----------
#         sales_entries = self.env['poultry.sale'].search(date_domain + branch_domain)
#         self.total_sales = sum(sales_entries.mapped('revenue'))
#
#         # ---------- Purchases ----------
#         purchase_entries = self.env['poultry.purchase'].search(date_domain + branch_domain)
#         self.total_purchases = sum(purchase_entries.mapped('total'))
#
#         # ---------- Expenses ----------
#         expense_entries = self.env['poultry.finance'].search(
#             date_domain + branch_domain + [('entry_type', '=', 'expense')])
#         self.total_expenses = sum(expense_entries.mapped('amount'))
#
#         # ---------- Salaries ----------
#
#     def _calculate_salaries(self):
#         """
#         Calculate total salaries based on active employees within the branch,
#         multiplied by the number of months in the selected date range.
#         """
#         self._validate_dates()
#
#         # Calculate number of months between start_date and end_date
#         delta = relativedelta(self.end_date, self.start_date)
#         months = (delta.years * 12) + delta.months + 1  # Inclusive
#
#         # Filter employees
#         domain = [('active', '=', True)]
#         if self.branch_id:
#             domain.append(('branch_id', '=', self.branch_id.id))
#
#         employees = self.env['poultry.employee'].search(domain)
#
#         # Sum all salaries
#         total_monthly_salaries = sum(employees.mapped('salary'))
#
#         # Multiply by number of months
#         total_salaries = total_monthly_salaries * months
#
#         return total_salaries
#
#         # ---------- Feed Cost ----------
#         feed_entries = self.env['poultry.feed'].search(date_domain + branch_domain)
#         self.total_feed = sum([f.quantity * (f.purchase_price or 0.0) for f in feed_entries])
#
#         # ---------- Medicine Cost ----------
#         medicine_entries = self.env['poultry.medicine'].search(date_domain + branch_domain)
#         self.total_medicine = sum([m.quantity * (m.purchase_price or 0.0) for m in medicine_entries])
#
#         # ---------- Vaccination Cost ----------
#         vaccination_cost_entries = self.env['poultry.finance'].search(
#             date_domain + branch_domain + [('description', 'ilike', 'Vaccination')]
#         )
#         self.total_vaccination = sum(vaccination_cost_entries.mapped('amount'))
#
#         # ---------- Net Profit ----------
#         self.net_profit = (
#                 self.total_income + self.total_sales
#                 - (
#                             self.total_purchases + self.total_expenses + self.total_salaries + self.total_feed + self.total_medicine + self.total_vaccination)
#         )
#
#     def compute_report(self):
#         self.generate_report()
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': self._name,
#             'view_mode': 'form',
#             'res_id': self.id,
#             'views': [(False, 'form')],
#             'target': 'new',  # keep it as popup
#         }
#
#     @api.onchange('start_date', 'end_date', 'branch_id')
#     def _onchange_generate_report(self):
#         self.generate_report()
#
#     # -------------------------------------------------------------------
#     # Step 2: Print PDF report
#     # -------------------------------------------------------------------
#     def print_pdf_report(self):
#         """Generate the PDF finance report"""
#         self.ensure_one()
#         self.generate_report()  # calculate totals
#         return self.env.ref('poultry_farm.action_poultry_finance_report').report_action(self)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

from datetime import date


class PoultryFinanceReport(models.TransientModel):
    _name = 'poultry.finance.report'
    _description = 'Comprehensive Poultry Finance Report Wizard'

    # -------------------------------
    # Filters
    # -------------------------------
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")

    # -------------------------------
    # Calculated Totals
    # -------------------------------
    total_income = fields.Monetary(string="Total Income", readonly=True)
    total_sales = fields.Monetary(string="Total Sales", readonly=True)
    total_purchases = fields.Monetary(string="Total Purchases", readonly=True)
    total_expenses = fields.Monetary(string="Total Expenses", readonly=True)
    total_salaries = fields.Monetary(string="Total Salaries", readonly=True)
    total_feed = fields.Monetary(string="Total Feed Cost", readonly=True)
    total_medicine = fields.Monetary(string="Total Medicine Cost", readonly=True)
    total_vaccination = fields.Monetary(string="Total Vaccination Cost", readonly=True)
    net_profit = fields.Monetary(string="Net Profit", readonly=True)

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )


    # -------------------------------
    # Helper: Validate dates
    # -------------------------------
    def _validate_dates(self):
        if not self.start_date or not self.end_date:
            raise UserError(_("Please provide both start and end dates."))

        if self.start_date > self.end_date:
            raise UserError(_("Start date cannot be after end date."))

    # -------------------------------
    # Helper: Build search domain
    # -------------------------------
    def _get_domain(self, date_field='date'):
        """Generic domain builder for date + branch filters"""
        domain = [(date_field, '>=', self.start_date), (date_field, '<=', self.end_date)]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        return domain

    # -------------------------------
    # Calculation Methods
    # -------------------------------
    # def _calculate_income(self):
    #     domain = self._get_domain('date') + [('entry_type', '=', 'income')]
    #     return self._sum_model('poultry.finance', domain, 'amount')
    def _calculate_income(self):
        total_sale = self._calculate_sales()
        total_expenses = self._calculate_expenses()
        return total_sale - total_expenses

    def _calculate_purchases(self):
        return self._sum_model('poultry.purchase', self._get_domain('date'), 'total')

    def _calculate_expenses(self):
        """
        Calculate total expenses as:
            total_purchases (from poultry.purchase) + total_salaries (from salary.payment)

        Uses the date domain returned by self._get_domain('date') for purchases
        and a translated domain (date -> salary_date) for salary.payment.
        """

        # base domain for purchases (assumes purchases use field 'date')
        base_domain = self._get_domain('date') or []

        # 1) Purchases: assume model poultry.purchase and monetary field usually 'total' or 'amount'
        purchases = self.env['poultry.purchase'].search(base_domain)
        total_purchases = 0.0
        for p in purchases:
            # try common field names in order
            total_purchases += float(getattr(p, 'total', 0.0) or getattr(p, 'amount', 0.0) or 0.0)

        # 2) Salaries: translate the date field in the domain from 'date' -> 'salary_date'
        salary_domain = []
        for item in base_domain:
            # domain item typical form: (field, operator, value)
            if isinstance(item, (list, tuple)) and len(item) >= 3:
                field_name, operator, value = item[0], item[1], item[2]
                if field_name == 'date':
                    field_name = 'salary_date'
                salary_domain.append((field_name, operator, value))
            else:
                # keep other domain clauses as-is (e.g. ('employee_id','=',id))
                salary_domain.append(item)

        salaries = self.env['salary.payment'].search(salary_domain)
        total_salaries = sum(float(r.amount or 0.0) for r in salaries)

        return total_purchases + total_salaries

    def _calculate_sales(self):
        return self._sum_model('poultry.sale', self._get_domain('date'), 'total')



    def _calculate_salaries(self):
        """
        Calculate total salaries from salary.payment model
        based on selected date range and optional branch filter.
        """
        self._validate_dates()

        # Build domain for salary.payment
        domain = [
            ('salary_date', '>=', self.start_date),
            ('salary_date', '<=', self.end_date),
        ]

        # If branch filter is applied → filter by employee branch
        if self.branch_id:
            domain.append(('employee_id.branch_id', '=', self.branch_id.id))

        # Search salary payments within date range
        payments = self.env['salary.payment'].search(domain)

        # Sum salary amounts
        total_salaries = sum(payments.mapped('amount'))

        return total_salaries


    def _calculate_feed_cost(self):
        feed_records = self.env['poultry.feed'].search(self._get_domain('date'))
        return sum(f.quantity * (f.purchase_price or 0.0) for f in feed_records)

    # def _calculate_feed_cost(self):
    #     """
    #     Calculate total feed cost from poultry.purchase
    #     where purchase_type = 'feed'.
    #     """
    #     domain = self._get_domain('date') + [
    #         ('purchase_type', '=', 'feed')
    #     ]
    #
    #     purchases = self.env['poultry.purchase'].search(domain)
    #
    #     # Total = quantity * price
    #     return sum(p.quantity * (p.unit_price or 0.0) for p in purchases)

    def _calculate_medicine_cost(self):
        medicine_records = self.env['poultry.medicine'].search(self._get_domain('date'))
        return sum(m.quantity * (m.purchase_price or 0.0) for m in medicine_records)

    def _calculate_vaccination_cost(self):
        domain = self._get_domain('date') + [('description', 'ilike', 'Vaccination')]
        return self._sum_model('poultry.finance', domain, 'amount')

    # -------------------------------
    # Helper: Sum field from model
    # -------------------------------
    def _sum_model(self, model_name, domain, field_name):
        """Uses read_group for performance"""
        grouped = self.env[model_name].read_group(domain, [field_name], [])
        return grouped[0][field_name] if grouped else 0.0

    # -------------------------------
    # Core Logic
    # -------------------------------
    def generate_report(self):
        self._validate_dates()

        # Compute each section
        self.total_income = self._calculate_income()
        self.total_sales = self._calculate_sales()
        self.total_purchases = self._calculate_purchases()
        self.total_expenses = self._calculate_expenses()
        self.total_salaries = self._calculate_salaries()
        self.total_feed = self._calculate_feed_cost()
        self.total_medicine = self._calculate_medicine_cost()
        self.total_vaccination = self._calculate_vaccination_cost()

        # Calculate net profit
        self.net_profit = (
            self.total_income + self.total_sales
            - (self.total_purchases + self.total_expenses + self.total_salaries +
               self.total_feed + self.total_medicine + self.total_vaccination)
        )

    # -------------------------------
    # Onchange auto-calculation
    # -------------------------------
    @api.onchange('start_date', 'end_date', 'branch_id')
    def _onchange_generate_report(self):
        if self.start_date and self.end_date:
            self.generate_report()

    # -------------------------------
    # Button: Show report in popup
    # -------------------------------
    def compute_report(self):
        self.generate_report()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    # -------------------------------
    # Button: Print PDF
    # -------------------------------
    def print_pdf_report(self):
        self.ensure_one()
        self.generate_report()  # Ensure latest values
        return self.env.ref('poultry_farm.action_poultry_finance_report').report_action(self)



#
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class PoultryFinanceReport(models.TransientModel):
#     _name = 'poultry.finance.report'
#     _description = 'Comprehensive Poultry Finance Report Wizard'
#
#     # ------------------------------------------------------------
#     # Wizard Fields
#     # ------------------------------------------------------------
#     start_date = fields.Date(string="Start Date", required=True)
#     end_date = fields.Date(string="End Date", required=True)
#     branch_id = fields.Many2one('poultry.branch', string="Branch")
#
#     # Computed Totals
#     total_income = fields.Monetary(string="Total Income", readonly=True)
#     total_sales = fields.Monetary(string="Total Sales", readonly=True)
#     total_purchases = fields.Monetary(string="Total Purchases", readonly=True)
#     total_expenses = fields.Monetary(string="Total Expenses", readonly=True)
#     total_salaries = fields.Monetary(string="Total Salaries", readonly=True)
#     total_feed = fields.Monetary(string="Total Feed Cost", readonly=True)
#     total_medicine = fields.Monetary(string="Total Medicine Cost", readonly=True)
#     total_vaccination = fields.Monetary(string="Total Vaccination Cost", readonly=True)
#     net_profit = fields.Monetary(string="Net Profit", readonly=True)
#
#     currency_id = fields.Many2one(
#         'res.currency',
#         default=lambda self: self.env.company.currency_id,
#         readonly=True
#     )
#
#     # ------------------------------------------------------------
#     # Validations
#     # ------------------------------------------------------------
#     @api.constrains('start_date', 'end_date')
#     def _check_dates(self):
#         for rec in self:
#             if rec.end_date and rec.start_date and rec.end_date < rec.start_date:
#                 raise ValidationError(_("End Date cannot be earlier than Start Date."))
#
#     # ------------------------------------------------------------
#     # Helper Functions
#     # ------------------------------------------------------------
#     def _base_domain(self, date_field='date'):
#         """
#         Builds a dynamic domain based on date range and branch.
#         """
#         domain = [
#             (date_field, '>=', self.start_date),
#             (date_field, '<=', self.end_date)
#         ]
#         if self.branch_id:
#             domain.append(('branch_id', '=', self.branch_id.id))
#         return domain
#
#     def _sum_field(self, model, domain, field_name):
#         """
#         Utility method to sum a specific field using read_group (optimized).
#         """
#         if not self.start_date or not self.end_date:
#             return 0.0
#
#         result = self.env[model].read_group(domain, [field_name], [])
#         return result[0][field_name] if result and field_name in result[0] else 0.0
#
#     # ------------------------------------------------------------
#     # Main Calculation
#     # ------------------------------------------------------------
#     def generate_report(self):
#         """
#         Calculate all totals for the finance report.
#         """
#         _logger.info("Generating poultry finance report for date range: %s to %s",
#                      self.start_date, self.end_date)
#
#         # Income
#         self.total_income = self._sum_field(
#             'poultry.finance',
#             self._base_domain('date') + [('entry_type', '=', 'income')],
#             'amount'
#         )
#
#         # Sales
#         self.total_sales = self._sum_field(
#             'poultry.sale',
#             self._base_domain('date'),
#             'revenue'
#         )
#
#         # Purchases
#         self.total_purchases = self._sum_field(
#             'poultry.purchase',
#             self._base_domain('date'),
#             'total'
#         )
#
#         # Expenses
#         self.total_expenses = self._sum_field(
#             'poultry.finance',
#             self._base_domain('date') + [('entry_type', '=', 'expense')],
#             'amount'
#         )
#
#         # Salaries
#         salary_domain = self._base_domain('payment_date')
#         salaries = self.env['poultry.salary'].search(salary_domain)
#         if self.branch_id:
#             salaries = salaries.filtered(lambda s: s.employee_id.branch_id == self.branch_id)
#         self.total_salaries = sum(salaries.mapped('amount'))
#
#         # Feed Cost
#         feed_domain = self._base_domain('date')
#         feeds = self.env['poultry.feed'].search(feed_domain)
#         self.total_feed = sum(f.quantity * (f.purchase_price or 0.0) for f in feeds)
#
#         # Medicine Cost
#         medicine_domain = self._base_domain('date')
#         medicines = self.env['poultry.medicine'].search(medicine_domain)
#         self.total_medicine = sum(m.quantity * (m.purchase_price or 0.0) for m in medicines)
#
#         # Vaccination Cost
#         self.total_vaccination = self._sum_field(
#             'poultry.finance',
#             self._base_domain('date') + [('description', 'ilike', 'Vaccination')],
#             'amount'
#         )
#
#         # Net Profit
#         self.net_profit = (
#             self.total_income + self.total_sales
#             - (self.total_purchases + self.total_expenses + self.total_salaries +
#                self.total_feed + self.total_medicine + self.total_vaccination)
#         )
#
#         _logger.info("Report Generated: Net Profit = %s", self.net_profit)
#
#     # ------------------------------------------------------------
#     # Actions
#     # ------------------------------------------------------------
#     def compute_report(self):
#         """
#         Compute and display the report in wizard popup form.
#         """
#         self.generate_report()
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': self._name,
#             'view_mode': 'form',
#             'res_id': self.id,
#             'target': 'new',
#         }
#
#     def print_pdf_report(self):
#         """
#         Generate PDF Finance Report
#         """
#         self.generate_report()
#         return self.env.ref('poultry_farm.action_poultry_finance_report').report_action(self)
#
#     @api.onchange('start_date', 'end_date', 'branch_id')
#     def _onchange_generate_report(self):
#         """
#         Automatically recalculate when filters are changed.
#         """
#         if self.start_date and self.end_date:
#             self.generate_report()
