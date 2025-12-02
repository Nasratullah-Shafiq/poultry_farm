from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalaryPaymentReport(models.TransientModel):
    _name = 'salary.payment.wizard'
    _description = 'Salary Payment Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")

    total_paid_amount = fields.Monetary(string="Total Salary Paid", readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    salary_lines = fields.One2many(
        'salary.payment.report.line',
        'wizard_id',
        string="Salary Details",
        readonly=True
    )

    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date.")

    def _get_domain(self):
        """Build domain for filtering salary payments."""
        domain = [
            ('salary_date', '>=', self.start_date),
            ('salary_date', '<=', self.end_date),
            ('payment_status', '=', 'paid'),
        ]
        if self.branch_id:
            domain.append(('employee_id.branch_id', '=', self.branch_id.id))

        return domain

    def generate_report(self):
        self.ensure_one()

        Salary = self.env['salary.payment']
        domain = self._get_domain()

        salaries = Salary.search(domain, order='salary_date asc')

        # Clear previous results
        self.salary_lines.unlink()

        total_paid = 0

        for sal in salaries:
            self.env['salary.payment.report.line'].create({
                'wizard_id': self.id,
                'salary_date': sal.salary_date,
                'employee_id': sal.employee_id.id,
                'branch_id': sal.employee_id.branch_id.id if sal.employee_id.branch_id else False,
                'amount': sal.amount,
            })
            total_paid += sal.amount

        self.total_paid_amount = total_paid

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'salary.payment.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def print_pdf_report(self):
        self.generate_report()
        return self.env.ref('poultry_farm.action_salary_payment_report').report_action(self)


class SalaryPaymentReportLine(models.TransientModel):
    _name = 'salary.payment.report.line'
    _description = 'Salary Payment Report Line'

    wizard_id = fields.Many2one(
        'salary.payment.wizard',  # Must match the wizard _name
        ondelete='cascade'
    )
    salary_date = fields.Date(string="Salary Date")
    employee_id = fields.Many2one('poultry.employee', string="Employee")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    amount = fields.Monetary(string="Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
