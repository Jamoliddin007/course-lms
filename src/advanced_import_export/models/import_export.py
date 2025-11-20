# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import csv
import base64
import io


class AdvancedImportExport(models.Model):
    _name = 'advanced.import.export'
    _description = 'Advanced Import Export'
    _rec_name = 'operation'

    # Basic fields
    operation = fields.Selection([
        ('export', 'Export'),
        ('import', 'Import')
    ], string='Operation', required=True, default='export')

    model_id = fields.Many2one('ir.model', string='Model', required=True,
                               domain=[('transient', '=', False)], ondelete="cascade")
    model_name = fields.Char(related='model_id.model', store=True)

    # Export
    export_data = fields.Binary(string='Download File', readonly=True)
    export_filename = fields.Char(string='Filename', default='export.csv')

    # Import
    import_data = fields.Binary(string='Upload File')
    import_filename = fields.Char(string='Filename')

    # Options
    include_id = fields.Boolean(string='Include ID', default=True)

    # Multi-language
    multi_lang = fields.Boolean(string='Multi-Language Export', default=False)
    lang_ids = fields.Many2many('res.lang', string='Languages')

    # Export action
    def action_export(self):
        self.ensure_one()

        if not self.model_name:
            raise UserError(_('Please select a model'))

        # Get all records
        Model = self.env[self.model_name]
        records = Model.search([])

        if not records:
            raise UserError(_('No records to export'))

        # Get fields
        field_names = self._get_exportable_fields()

        # CSV header
        headers = []
        if self.include_id:
            headers.append('id')

        for fname in field_names:
            if self.multi_lang and self.lang_ids:
                field = Model._fields.get(fname)
                if field and field.translate:
                    for lang in self.lang_ids:
                        headers.append(f"{fname}:{lang.code}")
                else:
                    headers.append(fname)
            else:
                headers.append(fname)

        # Build CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)

        for record in records:
            row = []
            if self.include_id:
                row.append(record.id)

            for fname in field_names:
                field = Model._fields.get(fname)

                if self.multi_lang and self.lang_ids and field.translate:
                    for lang in self.lang_ids:
                        val = record.with_context(lang=lang.code)[fname] or ''
                        row.append(val)
                else:
                    val = record[fname]
                    row.append(self._format_export_value(val, field.type))

            writer.writerow(row)

        # Save to binary
        csv_data = output.getvalue().encode('utf-8')
        self.export_data = base64.b64encode(csv_data)
        self.export_filename = f"{self.model_name}.csv"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Export completed'),
                'type': 'success',
            }
        }

    # Import action
    def action_import(self):
        self.ensure_one()

        if not self.import_data:
            raise UserError(_('Please upload a file'))

        # Decode CSV
        csv_data = base64.b64decode(self.import_data).decode('utf-8')
        csv_file = io.StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        Model = self.env[self.model_name]
        created = updated = errors = 0

        for row in reader:
            try:
                record_id = row.get('id', '').strip()
                vals = self._prepare_import_values(row, Model)

                if record_id and record_id.isdigit():
                    # Update
                    record = Model.browse(int(record_id))
                    if record.exists():
                        record.write(vals)
                        updated += 1
                    else:
                        raise UserError(f"Record ID {record_id} not found")
                else:
                    # Create
                    Model.create(vals)
                    created += 1

            except Exception as e:
                errors += 1
                continue

        message = f"Created: {created}, Updated: {updated}, Errors: {errors}"

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success' if errors == 0 else 'warning',
            }
        }

    # Helper methods
    def _get_exportable_fields(self):
        """Get exportable field names"""
        Model = self.env[self.model_name]
        exclude = ['create_uid', 'write_uid', 'create_date', 'write_date', '__last_update']

        fields = []
        for fname, field in Model._fields.items():
            if fname in exclude:
                continue
            if field.store and field.type not in ['one2many', 'binary']:
                fields.append(fname)

        return fields

    def _format_export_value(self, value, ftype):
        """Format value for CSV export"""
        if not value:
            return ''
        if ftype == 'many2one':
            return value.id
        if ftype == 'many2many':
            return ','.join(str(x) for x in value.ids)
        if ftype == 'boolean':
            return 'TRUE' if value else 'FALSE'
        if ftype in ['date', 'datetime']:
            return str(value)
        return str(value)

    def _prepare_import_values(self, row, Model):
        """Prepare values dict from CSV row"""
        vals = {}

        for key, value in row.items():
            if key == 'id' or not value:
                continue

            # Handle multi-lang: name:en_US
            if ':' in key:
                field_name, lang_code = key.split(':', 1)
                if field_name not in vals:
                    vals[field_name] = {}
                vals[field_name][lang_code] = value
            else:
                field = Model._fields.get(key)
                if field:
                    vals[key] = self._convert_import_value(value, field.type)

        # Apply translations
        for fname, translations in list(vals.items()):
            if isinstance(translations, dict):
                # Set default language first
                default_lang = self.env.lang or 'en_US'
                vals[fname] = translations.get(default_lang, list(translations.values())[0])

        return vals

    def _convert_import_value(self, value, ftype):
        """Convert CSV value to Odoo field type"""
        if not value:
            return False

        if ftype == 'integer':
            return int(value)
        if ftype == 'float':
            return float(value)
        if ftype == 'boolean':
            return value.upper() in ['TRUE', '1', 'YES']
        if ftype == 'many2one':
            return int(value)
        if ftype == 'many2many':
            ids = [int(x.strip()) for x in value.split(',')]
            return [(6, 0, ids)]

        return value