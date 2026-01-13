from odoo import models, fields, api
from odoo.exceptions import ValidationError

class DeadReportWizard(models.TransientModel):
    _name = 'dead.report.wizard'
    _description = 'Poultry Death Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)

    branch_id = fields.Many2one('poultry.branch', string="Branch")
    farm_id = fields.Many2one(
        'poultry.farm.house',
        string="Farm",
        domain="[('branch_id', '=', branch_id)]"
    )

    total_deaths = fields.Integer(string="Total Deaths", readonly=True)

    death_lines = fields.One2many(
        'dead.report.line',
        'wizard_id',
        string="Death Details",
        readonly=True
    )

    @api.constrains('start_date', 'end_date')
    def _check_date_range(self):
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date < rec.start_date:
                raise ValidationError("End Date cannot be earlier than Start Date.")

    def _get_domain(self):
        self.ensure_one()
        domain = [('date', '>=', self.start_date), ('date', '<=', self.end_date)]
        if self.branch_id:
            domain.append(('branch_id', '=', self.branch_id.id))
        if self.farm_id:
            domain.append(('farm_id', '=', self.farm_id.id))
        return domain

    def generate_report(self):
        self.ensure_one()
        Death = self.env['poultry.death']
        domain = self._get_domain()
        deaths = Death.search(domain, order='date asc')

        self.death_lines.unlink()

        total_deaths = 0
        for death in deaths:
            self.env['dead.report.line'].create({
                'wizard_id': self.id,
                'date': death.date,
                'branch_id': death.branch_id.id,
                'farm_id': death.farm_id.id,
                'item_type_id': death.item_type_id.id,
                'quantity': death.quantity,
                'reason': death.reason,
                'description': death.description,
            })
            total_deaths += death.quantity

        self.total_deaths = total_deaths

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dead.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def print_pdf_report(self):
        self.generate_report()
        return self.env.ref('poultry_farm.action_dead_report').report_action(self)



class DeadReportLine(models.TransientModel):
    _name = 'dead.report.line'
    _description = 'Poultry Death Report Line'

    wizard_id = fields.Many2one('dead.report.wizard', ondelete='cascade')
    date = fields.Date(string="Date")
    branch_id = fields.Many2one('poultry.branch', string="Branch")
    farm_id = fields.Many2one('poultry.farm.house', string="Farm")
    item_type_id = fields.Many2one('item.type', string="Type")
    quantity = fields.Integer(string="Quantity")
    reason = fields.Selection([
        ('disease', 'Disease'),
        ('injury', 'Injury'),
        ('natural', 'Natural Cause'),
        ('unknown', 'Unknown')
    ], string="Reason")
    description = fields.Text(string="Notes")

