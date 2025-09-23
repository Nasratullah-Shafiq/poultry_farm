class ReportPoultrySales(models.AbstractModel):
    _name = 'report.poultry_farm.report_poultry_sales_template'
    _description = 'Poultry Sales Report'

    def _get_report_values(self, docids, data=None):
        wizard = self.env['poultry.sale.report.wizard'].browse(docids)

        # Build domain
        domain = [
            ('date', '>=', wizard.start_date),
            ('date', '<=', wizard.end_date)
        ]
        if wizard.branch_id:
            domain.append(('branch_id', '=', wizard.branch_id.id))

        sales = self.env['poultry.sale'].search(domain)

        # Group by branch and poultry type
        grouped_sales = {}
        for sale in sales:
            branch = sale.branch_id.name
            poultry_type = sale.poultry_type_id.name

            if branch not in grouped_sales:
                grouped_sales[branch] = {}
            if poultry_type not in grouped_sales[branch]:
                grouped_sales[branch][poultry_type] = {'quantity': 0, 'revenue': 0}

            grouped_sales[branch][poultry_type]['quantity'] += sale.quantity
            grouped_sales[branch][poultry_type]['revenue'] += sale.revenue

        return {
            'doc_ids': docids,
            'doc_model': 'poultry.sale.report.wizard',
            'docs': wizard,
            'grouped_sales': grouped_sales,
        }
