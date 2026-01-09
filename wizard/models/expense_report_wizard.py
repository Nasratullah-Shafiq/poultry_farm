from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ExpenseReportWizard(models.TransientModel):
    _name = 'expense.report.wizard'
    _description = 'Branch and Farm Expense Report Wizard'

    # Filters
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

    # Summary
    total_expense_amount = fields.Float(
        string="Total Expenses",
        readonly=True
    )

    # Report lines
    expense_lines = fields.One2many(
        'expense.report.line',
        'wizard_id',
        string="Expense Details",
        readonly=True
    )

    # ----------------------------
    # Validations
    # ----------------------------
    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise ValidationError(
                    "End Date cannot be earlier than Start Date."
                )

    # ----------------------------
    # Domain Builder
    # ----------------------------
    def _get_domain(self):
        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
        ]

        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))

        if self.farm_id:
            domain.append(('farm_id', '=', self.farm_id.id))

        return domain

    # ----------------------------
    # Actions
    # ----------------------------
    def generate_report(self):
        self.ensure_one()

        Expense = self.env['poultry.expense']
        domain = self._get_domain()

        expenses = Expense.search(domain, order='date asc')

        # Clear previous data
        self.expense_lines.unlink()

        total = 0.0
        for exp in expenses:
            self.env['expense.report.line'].create({
                'wizard_id': self.id,
                'expense_date': exp.date,
                'branch_id': exp.branch_id.id,
                'farm_id': exp.farm_id.id,
                'expense_type_id': exp.expense_type_id.id,
                'amount': exp.amount,
            })
            total += exp.amount

        self.total_expense_amount = total

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'expense.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def print_pdf_report(self):
        self.generate_report()
        return self.env.ref(
            'poultry_farm.action_expense_report'
        ).report_action(self)


# ======================================================
# Report Line Model
# ======================================================
class ExpenseReportLine(models.TransientModel):
    _name = 'expense.report.line'
    _description = 'Expense Report Line'

    wizard_id = fields.Many2one(
        'expense.report.wizard',
        ondelete='cascade'
    )

    expense_date = fields.Date(string="Date")

    branch_id = fields.Many2one(
        'poultry.branch',
        string="Branch"
    )

    farm_id = fields.Many2one(
        'poultry.farm.house',
        string="Farm"
    )

    expense_type_id = fields.Many2one(
        'poultry.expense.type',
        string="Expense Type"
    )

    amount = fields.Float(string="Amount")



