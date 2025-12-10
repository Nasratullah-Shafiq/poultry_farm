# poultry_farm_management/models/branch.py
from odoo import models, fields

class PoultryBranch(models.Model):
    _name = 'poultry.branch'
    _description = 'Poultry Branch'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter

    name = fields.Char(required=True, tracking=True)  # track branch name changes
    code = fields.Char(tracking=True)  # track code updates
    address = fields.Text(tracking=True)  # track address changes
    manager_ids = fields.Many2one('res.users', string='Branch Manager')
    is_main = fields.Boolean(string='Is Main Branch', default=False)

    farm_ids = fields.One2many('poultry.farm.house', 'branch_id', string='Farms')


