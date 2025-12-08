from odoo import models, fields, api
from datetime import date, datetime, timedelta
import datetime



class PoultrySalary(models.Model):
    _name = 'salary.payment'
    _description = 'Employee Salary Payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(
        'poultry.employee', string='Employee', required=True
    )
    salary_date = fields.Date(string='Salary Date', required=True)
    amount_received = fields.Monetary(string='Amount Received', required=True, default=0)
    amount_remaining = fields.Monetary(
        string='Amount Remaining',
        compute='_compute_amount_remaining',
        store=True
    )
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id.id
    )
    total_salary = fields.Monetary(
        string='Total Salary',
        related='employee_id.salary',
        store=True
    )

    payment_status = fields.Selection(
        [
            ('not_paid', 'Not Paid'),
            ('partially_paid', 'Partially Paid'),
            ('paid', 'Paid'),
        ],
        string='Payment Status',
        compute='_compute_payment_status',
        store=True
    )

    notes = fields.Text(string='Notes')

    salary_month = fields.Selection(
        [
            ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
            ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        string="Month",
        compute="_compute_year_month",
        store=True
    )

    paid_this_month_display = fields.Monetary(
        string='',
        compute='_compute_previous_paid_amount',
        store=False  # no need to store since it’s dynamic
    )

    paid_month_label = fields.Char(
        compute='_compute_month_label',
        store=False
    )


    @api.depends('salary_date')
    def _compute_month_label(self):
        for rec in self:
            if rec.salary_date:
                month_name = rec.salary_date.strftime('%B')
                rec.paid_month_label = f"{month_name} Payment"
            else:
                rec.paid_month_label = "Paid This Month"

    # Year field as Selection
    def _get_year_selection(self):
        current_year = datetime.date.today().year
        return [(str(y), str(y)) for y in range(current_year - 10, current_year + 1)]

    salary_year = fields.Selection(
        selection=_get_year_selection,
        string="Year",
        compute="_compute_year_month",
        store=True
    )
    @api.depends('total_salary', 'amount_received', 'paid_this_month_display')
    def _compute_amount_remaining(self):
        for rec in self:
            # Remaining salary = total_salary - (previous paid + current payment)
            rec.amount_remaining = max(rec.total_salary - (rec.paid_this_month_display + rec.amount_received), 0)

    @api.depends('salary_date')
    def _compute_year_month(self):
        for rec in self:
            if rec.salary_date:
                rec.salary_year = str(rec.salary_date.year)
                rec.salary_month = str(rec.salary_date.month)
            else:
                rec.salary_year = False
                rec.salary_month = False



    @api.depends('employee_id', 'salary_date', 'amount_received')
    def _compute_previous_paid_amount(self):
        for rec in self:
            if not rec.employee_id or not rec.salary_date:
                rec.paid_this_month_display = 0  # <-- assign here
                rec.paid_this_month_display = "0"
                continue

            salary_date = rec.salary_date
            month_start = salary_date.replace(day=1)
            next_month = (month_start + timedelta(days=31)).replace(day=1)
            month_end = next_month - timedelta(days=1)

            # Calculate total paid in this month
            payments = self.env['salary.payment'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('salary_date', '>=', month_start),
                ('salary_date', '<=', month_end),
                ('id', '!=', rec.id or 0),
            ])
            # total_paid = sum(payments.mapped('amount_received'))
            #
            # # Assign computed values
            # rec.previous_paid_amount = total_paid
            # month_name = salary_date.strftime('%B')  # e.g., "January"
            # rec.paid_this_month_display = f"{month_name} Payment: {total_paid}"
            total_paid = sum(payments.mapped('amount_received'))

            rec.paid_this_month_display = total_paid

            # only the number
            rec.paid_this_month_display = str(total_paid)

    @api.depends('paid_this_month_display', 'previous_paid_amount', 'amount_received', 'amount_remaining',
                 'total_salary')
    def _compute_payment_status(self):
        for rec in self:
            # Safely obtain numeric value for "paid this month (previous)".
            # paid_this_month_display is a Char (string) used only for UI display in some setups,
            # so try to parse it to float; fallback to numeric previous_paid_amount.
            prev_paid = 0.0
            if getattr(rec, 'paid_this_month_display', False):
                try:
                    # remove commas and whitespace if any, then convert
                    prev_paid = float(str(rec.paid_this_month_display).replace(',', '').strip())
                except Exception:
                    prev_paid = float(rec.previous_paid_amount or 0.0)
            else:
                prev_paid = float(rec.previous_paid_amount or 0.0)

            # amount_received is the current row's payment (numeric)
            cur_paid = float(rec.amount_received or 0.0)

            # Note: depending on your desired semantics you might want to use total_paid = prev_paid + cur_paid
            # but you specifically requested checks based on `paid_this_month_display` first.
            total_paid_this_month = prev_paid + cur_paid

            # Use the numeric amount_remaining if present; otherwise compute it here
            rem = None
            if rec.amount_remaining is not None:
                rem = float(rec.amount_remaining or 0.0)
            else:
                # fallback compute
                rem = max(float(rec.total_salary or 0.0) - total_paid_this_month, 0.0)

            # Apply rules in the order you requested
            if prev_paid == 0.0:
                rec.payment_status = 'not_paid'
            elif rem > 0.0:
                rec.payment_status = 'partially_paid'
            elif rem == 0.0 and (rec.total_salary or 0.0) > 0.0:
                rec.payment_status = 'paid'
            else:
                # Fallback: if nothing matched, mark partially_paid (safe default)
                rec.payment_status = 'partially_paid'

    # @api.depends('total_salary', 'amount_received')
    # def _compute_payment_status(self):
    #     for rec in self:
    #         if rec.amount_received <= 0:
    #             rec.payment_status = 'not_paid'
    #         elif rec.amount_received < rec.total_salary:
    #             rec.payment_status = 'partially_paid'
    #         else:
    #             rec.payment_status = 'paid'
