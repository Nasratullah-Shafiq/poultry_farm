
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CustomerPaymentReportWizard(models.TransientModel):
    _name = 'customer.payment.report.wizard'
    _description = 'Customer Payment Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    branch_id = fields.Many2one('poultry.branch', string="Branch")
    customer_id = fields.Many2one('poultry.partner', string="Customer",domain=[('partner_type', '=', 'customer')])

    total_sale = fields.Monetary(string="Total Sale", readonly=True)
    total_payment = fields.Monetary(string="Total Payment", readonly=True)
    total_due = fields.Monetary(string="Total Due", readonly=True)

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )
    payment_lines = fields.One2many('customer.payment.report.line', 'wizard_id', string="Payment Details", readonly=True)

    # -----------------------------
    # Validation
    # -----------------------------
    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date.")

    # -----------------------------
    # Domain Builder
    # -----------------------------
    def _get_domain(self):
        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date),
            ('partner_type', '=', 'customer'),
            ('payment_status', '=', 'done')
        ]

        if self.branch_id:
            domain.append(('to_branch_id', '=', self.branch_id.id))

        if self.customer_id:
            domain.append(('partner_id', '=', self.customer_id.id))

        return domain

    # -----------------------------
    # Generate Report
    # -----------------------------
    def generate_report(self):
        self.ensure_one()
        Payment = self.env['poultry.payment']
        payments = Payment.search(self._get_domain(), order='date asc')

        self.payment_lines.unlink()

        total_sale = 0.0
        total_payment = 0.0

        # Collect unique customers to calculate sale totals
        customers = payments.mapped('partner_id')

        for cust in customers:
            # Total sale for this customer
            customer_sales = self.env['poultry.sale'].search([
                ('customer_id', '=', cust.id),
                ('status', '=', 'sale_done')
            ])
            sale_total = sum(customer_sales.mapped('total'))

            # Total payment for this customer within date range
            customer_payments = payments.filtered(lambda p: p.partner_id == cust)
            payment_total = sum(customer_payments.mapped('amount'))

            # Create report lines
            for pay in customer_payments:
                self.env['customer.payment.report.line'].create({
                    'wizard_id': self.id,
                    'date': pay.date,
                    'partner_id': pay.partner_id.id,
                    'branch_id': pay.to_branch_id.id,
                    'account_id': pay.to_account_id.id,
                    'amount': pay.amount,
                    'note': pay.note,
                })

            total_sale += sale_total
            total_payment += payment_total

        self.total_sale = total_sale
        self.total_payment = total_payment
        self.total_due = total_sale - total_payment

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'customer.payment.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    # -----------------------------
    # Print PDF
    # -----------------------------
    def print_pdf_report(self):
        self.ensure_one()
        self.generate_report()
        return self.env.ref(
            'poultry_farm.action_customer_payment_report'
        ).report_action(self)


class CustomerPaymentReportLine(models.TransientModel):
    _name = 'customer.payment.report.line'
    _description = 'Customer Payment Report Line'

    wizard_id = fields.Many2one(
        'customer.payment.report.wizard',
        ondelete='cascade'
    )

    date = fields.Date(string="Date")
    partner_id = fields.Many2one('poultry.partner', string="Customer")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    account_id = fields.Many2one('poultry.cash.account', string="Cash Account")
    amount = fields.Monetary(string="Amount", currency_field='currency_id')
    note = fields.Text(string="Note")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)