from odoo import models, fields
from mako.template import Template
import os


class XMLGenerate(models.TransientModel):
    _name = "xml.generate"
    _description = "XML Generate"

    module_path = fields.Char(string="Module Path", required=True)
    model_ids = fields.Many2many("ir.model", string="Models", required=True)

    def generate(self):
        self.ensure_one()

        system_fields = {
            "id", "create_uid", "create_date", "write_uid", "write_date",
            "__last_update", "display_name"
        }

        for model in self.model_ids:
            model_name = model.model
            model_short = model_name.replace(".", "_")

            fields_data = []
            for f in model.field_id:
                if (
                    f.name not in system_fields and f.required
                ):
                    fields_data.append({"name": f.name, "required": f.required})

            template_path = os.path.join(
                os.path.dirname(__file__), "../templates/view_template.mako"
            )
            with open(template_path, "r", encoding="utf-8") as f:
                template_text = f.read()

            xml_content = Template(template_text).render(
                model_name=model_name,
                model_short=model_short,
                fields=fields_data,
            )

            output_dir = os.path.join(self.module_path, "views")
            os.makedirs(output_dir, exist_ok=True)

            output_file = os.path.join(output_dir, f"{model_short}.xml")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xml_content)

            print(f"XML generated for {model_name}: {output_file}")
