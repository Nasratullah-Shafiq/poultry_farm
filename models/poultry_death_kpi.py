# from odoo import models, fields, tools
#
#
# class PoultryDeathKPI(models.Model):
#     _name = 'poultry.death.kpi'
#     _description = 'Poultry Death KPIs'
#     _auto = False
#     _rec_name = 'name'
#
#     name = fields.Char()
#     value = fields.Integer()
#     icon = fields.Char()
#     color = fields.Char()
#
#     def init(self):
#         tools.drop_view_if_exists(self.env.cr, 'poultry_death_kpi')
#         self.env.cr.execute("""
#             CREATE OR REPLACE VIEW poultry_death_kpi AS (
#
#                 -- Last 24 Hours
#                 SELECT
#                     1 AS id,
#                     'Last 24 Hours Death' AS name,
#                     COALESCE(SUM(quantity), 0) AS value,
#                     'fa-clock' AS icon,
#                     '#dc3545' AS color
#                 FROM poultry_death
#                 WHERE date >= (CURRENT_DATE - INTERVAL '1 day')
#
#                 UNION ALL
#
#                 -- Current Month
#                 SELECT
#                     2 AS id,
#                     'Current Month Death' AS name,
#                     COALESCE(SUM(quantity), 0) AS value,
#                     'fa-calendar' AS icon,
#                     '#fd7e14' AS color
#                 FROM poultry_death
#                 WHERE date >= date_trunc('month', CURRENT_DATE)
#
#                 UNION ALL
#
#                 -- Current Year
#                 SELECT
#                     3 AS id,
#                     'Current Year Death' AS name,
#                     COALESCE(SUM(quantity), 0) AS value,
#                     'fa-chart-bar' AS icon,
#                     '#0d6efd' AS color
#                 FROM poultry_death
#                 WHERE date >= date_trunc('year', CURRENT_DATE)
#             )
#         """)

from odoo import models, fields, tools

class PoultryDeathKPI(models.Model):
    _name = 'poultry.death.kpi'
    _description = 'Poultry Death KPIs'
    _auto = False
    _rec_name = 'name'

    name = fields.Char(readonly=True)
    value = fields.Integer(readonly=True)
    icon = fields.Char(readonly=True)
    color = fields.Char(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute("""
            CREATE VIEW poultry_death_kpi AS (

                -- Last 24 Hours
                SELECT
                    1 AS id,
                    'Last 24 Hours Deaths' AS name,
                    COUNT(*) AS value,
                    'fa-calendar' AS icon,
                    '#e74c3c' AS color
                FROM poultry_death
                WHERE create_date >= NOW() - INTERVAL '24 HOURS'

                UNION ALL

                -- Current Month
                SELECT
                    2 AS id,
                    'Current Month Deaths' AS name,
                    COUNT(*) AS value,
                    'fa-calendar' AS icon,
                    '#f39c12' AS color
                FROM poultry_death
                WHERE date_trunc('month', create_date) = date_trunc('month', CURRENT_DATE)

                UNION ALL

                -- Current Year
                SELECT
                    3 AS id,
                    'Current Year Deaths' AS name,
                    COUNT(*) AS value,
                    'fa-calendar' AS icon,
                    '#c0392b' AS color
                FROM poultry_death
                WHERE date_trunc('year', create_date) = date_trunc('year', CURRENT_DATE)

            )
        """)

