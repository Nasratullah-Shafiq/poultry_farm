# from odoo import models, fields, api, _
# from odoo.exceptions import UserError
#
#
# class PoultryFinanceReport(models.TransientModel):
#     _name = 'poultry.finance.report'
#     _description = 'Comprehensive Poultry Finance Report Wizard'
#
#     # -------------------------------------------------
#     # Filters
#     # -------------------------------------------------
#     start_date = fields.Date(string="Start Date", required=True)
#     end_date = fields.Date(string="End Date", required=True)
#     branch_id = fields.Many2one('poultry.branch', string="Branch")
#
#     # -------------------------------------------------
#     # Totals
#     # -------------------------------------------------
#     total_income = fields.Monetary(string="Total Income", readonly=True)
#     total_sales = fields.Monetary(string="Total Sales", readonly=True)
#     total_purchases = fields.Monetary(string="Total Purchases", readonly=True)
#     total_expenses = fields.Monetary(string="Total Expenses", readonly=True)
#     total_salaries = fields.Monetary(string="Total Salaries", readonly=True)
#
#     # Expense by type
#     total_expense_by_type = fields.Monetary(
#         string="Total Expenses (All Types)",
#         readonly=True
#     )
#
#     total_expense_by_type_text = fields.Text(
#         string="Expense Breakdown by Type",
#         readonly=True
#     )
#
#     net_profit = fields.Monetary(string="Net Profit", readonly=True)
#
#     currency_id = fields.Many2one(
#         'res.currency',
#         default=lambda self: self.env.company.currency_id,
#         readonly=True
#     )
#
#     # -------------------------------------------------
#     # Validation
#     # -------------------------------------------------
#     def _validate_dates(self):
#         if not self.start_date or not self.end_date:
#             raise UserError(_("Please provide both start and end dates."))
#         if self.start_date > self.end_date:
#             raise UserError(_("Start date cannot be after end date."))
#
#     # -------------------------------------------------
#     # Domains
#     # -------------------------------------------------
#     def _get_domain(self, date_field='date'):
#         domain = [
#             (date_field, '>=', self.start_date),
#             (date_field, '<=', self.end_date),
#         ]
#         if self.branch_id:
#             domain.append(('branch_id', '=', self.branch_id.id))
#         return domain
#
#     # -------------------------------------------------
#     # Calculations
#     # -------------------------------------------------
#     def _calculate_sales(self):
#         return self._sum_model('poultry.sale', self._get_domain('date'), 'total')
#
#     def _calculate_purchases(self):
#         return self._sum_model('poultry.purchase', self._get_domain('date'), 'total')
#
#     def _calculate_salaries(self):
#         domain = [
#             ('salary_date', '>=', self.start_date),
#             ('salary_date', '<=', self.end_date),
#         ]
#
#         if self.branch_id:
#             employees = self.env['poultry.employee'].search([
#                 ('branch_id', '=', self.branch_id.id)
#             ])
#             domain.append(('employee_id', 'in', employees.ids))
#             # domain.append(('employee_id.branch_id', '=', self.branch_id.id))
#
#         payments = self.env['salary.payment'].search(domain)
#         return sum(payments.mapped('amount'))
#
#     def _calculate_expenses(self):
#         return self._calculate_purchases() + self._calculate_salaries()
#
#     def _calculate_income(self):
#         return self._calculate_sales() - self._calculate_expenses()
#
#     # -------------------------------------------------
#     # Expense by Type (CORE REQUIREMENT)
#     # -------------------------------------------------
#     def _compute_total_expense_by_type(self):
#         for rec in self:
#             rec.total_expense_by_type = 0.0
#             rec.total_expense_by_type_text = ""
#
#             if not rec.start_date or not rec.end_date:
#                 continue
#
#             domain = [
#                 ('date', '>=', rec.start_date),
#                 ('date', '<=', rec.end_date),
#             ]
#             if rec.branch_id:
#                 domain.append(('branch_id', '=', rec.branch_id.id))
#
#             expenses = self.env['poultry.expense'].search(domain)
#
#             totals = {}
#             total_amount = 0.0
#
#             for exp in expenses:
#                 name = exp.expense_type_id.name
#                 totals[name] = totals.get(name, 0.0) + exp.amount
#                 total_amount += exp.amount
#
#             rec.total_expense_by_type = total_amount
#
#             lines = []
#             for etype, amount in totals.items():
#                 lines.append(f"Total {etype}: {amount:.2f}")
#
#             rec.total_expense_by_type_text = "\n".join(lines)
#
#     # -------------------------------------------------
#     # Helpers
#     # -------------------------------------------------
#     def _sum_model(self, model_name, domain, field_name):
#         grouped = self.env[model_name].read_group(domain, [field_name], [])
#         return grouped[0][field_name] if grouped else 0.0
#
#     # -------------------------------------------------
#     # Main Logic
#     # -------------------------------------------------
#     def generate_report(self):
#         self._validate_dates()
#
#         self.total_sales = self._calculate_sales()
#         self.total_purchases = self._calculate_purchases()
#         self.total_salaries = self._calculate_salaries()
#         self.total_expenses = self._calculate_expenses()
#         self.total_income = self._calculate_income()
#
#         self._compute_total_expense_by_type()
#
#         self.net_profit = (
#             self.total_income
#             - (self.total_expenses + self.total_expense_by_type)
#         )
#
#     # -------------------------------------------------
#     # Onchange
#     # -------------------------------------------------
#     @api.onchange('start_date', 'end_date', 'branch_id')
#     def _onchange_generate_report(self):
#         if self.start_date and self.end_date:
#             self.generate_report()
#
#     # -------------------------------------------------
#     # Buttons
#     # -------------------------------------------------
#     def compute_report(self):
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
#         self.ensure_one()
#         self.generate_report()
#         return self.env.ref(
#             'poultry_farm.action_poultry_finance_report'
#         ).report_action(self)
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PoultryFinanceReport(models.TransientModel):
    _name = 'poultry.finance.report'
    _description = 'Comprehensive Poultry Finance Report Wizard'

    # -------------------------------------------------
    # Filters
    # -------------------------------------------------
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    branch_id = fields.Many2one(
        'poultry.branch',
        string="Branch"
    )

    farm_id = fields.Many2one(
        'poultry.farm.house',
        string="Farm",
        domain="[('branch_id', '=', branch_id)]"
    )

    # -------------------------------------------------
    # Totals
    # -------------------------------------------------
    total_sales = fields.Monetary(string="Total Sales", readonly=True)
    total_purchases = fields.Monetary(string="Total Purchases", readonly=True)
    total_salaries = fields.Monetary(string="Total Salaries", readonly=True)
    total_expenses = fields.Monetary(string="Total Expenses", readonly=True)
    total_income = fields.Monetary(string="Total Income", readonly=True)

    total_expense_by_type = fields.Monetary(
        string="Total Expenses (All Types)",
        readonly=True
    )

    total_expense_by_type_text = fields.Text(
        string="Expense Breakdown by Type",
        readonly=True
    )

    net_profit = fields.Monetary(string="Net Profit", readonly=True)

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    # -------------------------------------------------
    # Validation
    # -------------------------------------------------
    def _validate_dates(self):
        if not self.start_date or not self.end_date:
            raise UserError(_("Please provide both start and end dates."))
        if self.start_date > self.end_date:
            raise UserError(_("Start date cannot be after end date."))

    # -------------------------------------------------
    # Domain Builder
    # -------------------------------------------------
    def _get_domain(self, date_field='date'):
        domain = [
            (date_field, '>=', self.start_date),
            (date_field, '<=', self.end_date),
        ]

        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))

        if self.farm_id:
            domain.append(('farm_id', '=', self.farm_id.id))

        return domain

    # -------------------------------------------------
    # Calculations
    # -------------------------------------------------
    def _calculate_sales(self):
        return self._sum_model('poultry.sale', self._get_domain('date'), 'total')

    def _calculate_purchases(self):
        return self._sum_model('poultry.purchase', self._get_domain('date'), 'total')

    def _calculate_salaries(self):
        self._validate_dates()

        payment_domain = [
            ('salary_date', '>=', self.start_date),
            ('salary_date', '<=', self.end_date),
        ]

        employee_domain = []

        if self.branch_id:
            employee_domain.append(('branch_id', '=', self.branch_id.id))

        if self.farm_id:
            employee_domain.append(('farm_id', '=', self.farm_id.id))

        if employee_domain:
            employees = self.env['poultry.employee'].search(employee_domain)
            payment_domain.append(('employee_id', 'in', employees.ids))

        payments = self.env['salary.payment'].search(payment_domain)
        return sum(payments.mapped('amount'))

    def _calculate_expenses(self):
        return self._calculate_purchases() + self._calculate_salaries()

    def _calculate_income(self):
        return self._calculate_sales() - self._calculate_expenses()

    # -------------------------------------------------
    # Expense by Type
    # -------------------------------------------------
    def _compute_total_expense_by_type(self):
        for rec in self:
            rec.total_expense_by_type = 0.0
            rec.total_expense_by_type_text = ""

            if not rec.start_date or not rec.end_date:
                continue

            domain = [
                ('date', '>=', rec.start_date),
                ('date', '<=', rec.end_date),
            ]

            if rec.branch_id:
                domain.append(('branch_id', '=', rec.branch_id.id))

            if rec.farm_id:
                domain.append(('farm_id', '=', rec.farm_id.id))

            expenses = self.env['poultry.expense'].search(domain)

            totals = {}
            total_amount = 0.0

            for exp in expenses:
                name = exp.expense_type_id.name
                totals[name] = totals.get(name, 0.0) + exp.amount
                total_amount += exp.amount

            rec.total_expense_by_type = total_amount
            rec.total_expense_by_type_text = "\n".join(
                f"Total {k}: {v:.2f}" for k, v in totals.items()
            )

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------
    def _sum_model(self, model_name, domain, field_name):
        grouped = self.env[model_name].read_group(domain, [field_name], [])
        return grouped[0][field_name] if grouped else 0.0

    # -------------------------------------------------
    # Main Logic
    # -------------------------------------------------
    def generate_report(self):
        self._validate_dates()

        self.total_sales = self._calculate_sales()
        self.total_purchases = self._calculate_purchases()
        self.total_salaries = self._calculate_salaries()
        self.total_expenses = self._calculate_expenses()
        self.total_income = self._calculate_income()

        self._compute_total_expense_by_type()

        self.net_profit = (
            self.total_income
            - (self.total_expenses + self.total_expense_by_type)
        )

    # -------------------------------------------------
    # Onchange
    # -------------------------------------------------
    @api.onchange('start_date', 'end_date', 'branch_id', 'farm_id')
    def _onchange_generate_report(self):
        if self.start_date and self.end_date:
            self.generate_report()

    # -------------------------------------------------
    # Buttons
    # -------------------------------------------------
    def compute_report(self):
        self.generate_report()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def print_pdf_report(self):
        self.ensure_one()
        self.generate_report()
        return self.env.ref(
            'poultry_farm.action_poultry_finance_report'
        ).report_action(self)
