# poultry_farm_management/models/branch.py
from odoo import models, fields

class PoultryBranch(models.Model):
    _name = 'poultry.branch'
    _description = 'Poultry Branch'

    name = fields.Char(required=True)
    code = fields.Char()
    address = fields.Text()
    manager_ids = fields.Many2one('res.users', string='Branch Manager')
    is_main = fields.Boolean(string='Is Main Branch', default=False)
