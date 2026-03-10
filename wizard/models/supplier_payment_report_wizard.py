from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SupplierPaymentReportWizard(models.TransientModel):
    _name = 'supplier.payment.report.wizard'
    _description = 'Supplier Payment Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    branch_id = fields.Many2one('poultry.branch', string="Branch")
    supplier_id = fields.Many2one(
        'poultry.partner',
        string="Supplier",
        domain=[('partner_type', '=', 'supplier')]
    )

    total_purchase = fields.Monetary(string="Total Purchase", readonly=True)
    total_payment = fields.Monetary(string="Total Paid", readonly=True)
    total_due = fields.Monetary(string="Total Due", readonly=True)

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    payment_lines = fields.One2many(
        'supplier.payment.report.line',
        'wizard_id',
        string="Payment Details",
        readonly=True
    )

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
            ('partner_type', '=', 'supplier'),
            ('payment_status', '=', 'done')
        ]
        if self.branch_id:
            domain.append(('to_branch_id', '=', self.branch_id.id))
        if self.supplier_id:
            domain.append(('partner_id', '=', self.supplier_id.id))
        return domain

    # -----------------------------
    # Generate Report
    # -----------------------------
    def generate_report(self):
        self.ensure_one()
        Payment = self.env['poultry.payment']
        payments = Payment.search(self._get_domain(), order='date asc')

        self.payment_lines.unlink()
        total_payment = 0.0
        total_purchase = 0.0

        # Collect unique suppliers to calculate purchase totals
        suppliers = payments.mapped('partner_id')

        for sup in suppliers:
            # Total purchase for this supplier
            supplier_purchases = self.env['poultry.purchase'].search([
                ('supplier_id', '=', sup.id),
                ('status', '=', 'purchase_done')
            ])
            purchase_total = sum(supplier_purchases.mapped('total'))  # Sum of purchase totals

            # Total payment for this supplier within date range
            supplier_payments = payments.filtered(lambda p: p.partner_id == sup)
            payment_total = sum(supplier_payments.mapped('amount'))

            # Create report lines
            for pay in supplier_payments:
                self.env['supplier.payment.report.line'].create({
                    'wizard_id': self.id,
                    'date': pay.date,
                    'supplier_id': pay.partner_id.id,
                    'branch_id': pay.to_branch_id.id,
                    'account_id': pay.to_account_id.id,
                    'amount': pay.amount,
                    'note': pay.note,
                    'total_purchase': purchase_total,
                })

            total_payment += payment_total
            total_purchase += purchase_total

        self.total_payment = total_payment
        self.total_purchase = total_purchase
        self.total_due = total_purchase - total_payment

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'supplier.payment.report.wizard',
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
        return self.env.ref('poultry_farm.action_supplier_payment_report').report_action(self)


class SupplierPaymentReportLine(models.TransientModel):
    _name = 'supplier.payment.report.line'
    _description = 'Supplier Payment Report Line'

    wizard_id = fields.Many2one(
        'supplier.payment.report.wizard',
        ondelete='cascade'
    )
    date = fields.Date(string="Date")
    supplier_id = fields.Many2one('poultry.partner', string="Supplier")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    account_id = fields.Many2one('poultry.cash.account', string="Cash Account")
    amount = fields.Monetary(string="Paid Amount", currency_field='currency_id')
    total_purchase = fields.Monetary(string="Total Purchase", currency_field='currency_id')
    note = fields.Text(string="Note")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)