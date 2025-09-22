
from odoo import models, fields, api
from datetime import date, timedelta


class PoultryType(models.Model):
    _name = 'poultry.type'
    _description = 'Poultry Type'
    _rec_name = 'name'

    name = fields.Char(string="Type Name", required=True)
    description = fields.Text(string="Description")


class Poultry(models.Model):
    _name = 'poultry.farm'
    _description = 'Poultry Record'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Add chatter support

    name = fields.Char(string="Name", required=True)
    age = fields.Integer(string="Age (Weeks)", required=True)

    gender = fields.Selection(
        [
            ('male', 'Male'),
            ('female', 'Female')
        ],
        string="Gender",
        required=True
    )

    poultry_type_id = fields.Many2one(
        'poultry.type',
        string='Poultry Type',
        required=True,
        help="Select the type of poultry, e.g., Broiler, Layer, Duck, etc."
    )

    branch_id = fields.Many2one(
        'poultry.branch',
        string='Branch',
        help="The branch where this poultry is located"
    )

    description = fields.Text(string="Description")
    date_added = fields.Date(string="Date Added", default=fields.Date.today)

    # Computed field for search panel
    date_category = fields.Selection(
        [
            ('today', 'Today'),
            ('week', 'This Week'),
            ('month', 'This Month'),
            ('older', 'Older'),
        ],
        string="Date Category",
        compute="_compute_date_category",
        store=True
    )

    @api.depends('date_added')
    def _compute_date_category(self):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        for record in self:
            if not record.date_added:
                record.date_category = False
            elif record.date_added == today:
                record.date_category = 'today'
            elif record.date_added >= week_start:
                record.date_category = 'week'
            elif record.date_added >= month_start:
                record.date_category = 'month'
            else:
                record.date_category = 'older'

    class PoultryFarm(models.Model):
        _name = 'poultry.farm'
        _description = 'Poultry Farm Record'

        name = fields.Char(string="Poultry Name", required=True)
        age = fields.Integer(string="Age")
        gender = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female'),
        ], string="Gender")
        poultry_type_id = fields.Many2one('poultry.type', string="Poultry Type")
        branch_id = fields.Many2one('poultry.branch', string="Branch")
        date_added = fields.Date(string="Date Added", default=fields.Date.today)



