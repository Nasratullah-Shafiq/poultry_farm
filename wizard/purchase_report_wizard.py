from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PoultryPurchaseReport(models.TransientModel):
    _name = 'poultry.purchase.report'
    _description = 'Poultry Purchase Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    branch_id = fields.Many2one('poultry.branch', string="Branch")

    total_quantity = fields.Float(string="Total Quantity", readonly=True)
    total_amount = fields.Monetary(string="Total Amount", readonly=True)
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    purchase_lines = fields.One2many(
        'poultry.purchase.report.line',
        'wizard_id',
        string="Purchase Details",
        readonly=True
    )

    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date.")

    def _get_domain(self):
        """Build a search domain based on selected filters."""
        domain = [
            ('date', '>=', self.start_date),
            ('date', '<=', self.end_date)
        ]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        return domain

    def generate_report(self):
        """Fetch and compute purchase totals and details."""
        self.ensure_one()

        domain = self._get_domain()
        Purchase = self.env['poultry.purchase']

        # Fetch all matching purchases
        purchases = Purchase.search(domain, order='date asc')

        # Clear existing lines
        self.purchase_lines.unlink()

        total_qty = 0
        total_amount = 0

        # Create report lines for display and print
        for purchase in purchases:
            self.env['poultry.purchase.report.line'].create({
                'wizard_id': self.id,
                'date': purchase.date,
                'branch_id': purchase.branch_id.id,
                'item_type_id': purchase.item_type_id.id,
                'quantity': purchase.quantity,
                'unit_price': purchase.unit_price,
                'total': purchase.total,
                'supplier_id': purchase.supplier_id.id,
            })
            total_qty += purchase.quantity
            total_amount += purchase.total

        self.total_quantity = total_qty
        self.total_amount = total_amount

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'poultry.purchase.report',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def print_pdf_report(self):
        """Generate PDF purchase report."""
        self.generate_report()
        return self.env.ref('poultry_farm.action_poultry_purchase_report').report_action(self)


class PoultryPurchaseReportLine(models.TransientModel):
    _name = 'poultry.purchase.report.line'
    _description = 'Poultry Purchase Report Line'

    wizard_id = fields.Many2one('poultry.purchase.report', ondelete='cascade')
    date = fields.Date(string="Date")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    item_type_id = fields.Many2one('item.type', string="Type")
    quantity = fields.Float(string="Quantity")
    unit_price = fields.Monetary(string="Unit Price", currency_field='currency_id')
    total = fields.Monetary(string="Total", currency_field='currency_id')
    supplier_id = fields.Many2one('poultry.supplier', string="Supplier")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
