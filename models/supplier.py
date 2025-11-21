from odoo import models, fields

class PoultrySupplier(models.Model):
    _name = 'poultry.supplier'
    _description = 'Poultry Supplier'

    name = fields.Char(string='Supplier Name', required=True)
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')

    # Optional: show linked purchases in supplier form
    purchase_ids = fields.One2many('poultry.purchase', 'supplier_id', string='Purchases')
