# poultry_farm_management/models/branch.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError   # <-- Add this line


class PoultryBranch(models.Model):
    _name = 'poultry.branch'
    _description = 'Poultry Branch'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable chatter

    name = fields.Char(required=True, tracking=True)  # track branch name changes
    code = fields.Char(string='Branch Code', tracking=True, readonly=True)
    address = fields.Text(tracking=True)  # track address changes
    manager_ids = fields.Many2one('res.users', string='Branch Manager')
    is_main = fields.Boolean(string='Is Main Branch', default=False)

    farm_ids = fields.One2many('poultry.farm.house', 'branch_id', string='Farms')

    farm_names_list = fields.Char(
        string="Farm Names List",
        compute="_compute_farm_names_list",
        store=True
    )

    @api.depends('farm_ids.name')
    def _compute_farm_names_list(self):
        for branch in self:
            # Store farm names separated by a comma
            branch.farm_names_list = ','.join(branch.farm_ids.mapped('name')) if branch.farm_ids else ''


    class PoultryBranch(models.Model):
        _name = 'poultry.branch'
        _description = 'Poultry Branch'
        _inherit = ['mail.thread', 'mail.activity.mixin']

        name = fields.Char(required=True, tracking=True)
        code = fields.Char(string='Branch Code', tracking=True, readonly=True)
        address = fields.Text(tracking=True)
        manager_ids = fields.Many2one('res.users', string='Branch Manager')
        is_main = fields.Boolean(string='Is Main Branch', default=False)
        farm_ids = fields.One2many('poultry.farm.house', 'branch_id', string='Farms')



    @api.model
    def create(self, vals):
        # 1️⃣ Prevent duplicate branch name
        if vals.get('name'):
            existing_branch = self.search([('name', '=', vals['name'])], limit=1)
            if existing_branch:
                raise UserError(_('Branch with name "%s" already exists.') % vals['name'])

        # 2️⃣ Auto-generate branch code
        if not vals.get('code') and vals.get('name'):
            # Take first 3 letters of name, uppercase, no spaces
            prefix = vals['name'].replace(' ', '').upper()[:3]

            # Search last branch **globally**, order by numeric part
            last_branch = self.search([('code', '!=', False)], order='id desc', limit=1)

            if last_branch and last_branch.code and '-' in last_branch.code:
                try:
                    last_number = int(last_branch.code.split('-')[1])
                except:
                    last_number = 0
                new_number = str(last_number + 1).zfill(3)
            else:
                new_number = '001'

            vals['code'] = f'{prefix}-{new_number}'

        return super(PoultryBranch, self).create(vals)




