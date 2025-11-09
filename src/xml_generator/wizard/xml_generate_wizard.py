from odoo import models, fields, api
from mako.template import Template
import os


class XMLGenerate(models.TransientModel):
    _name = "xml.generate"
    _description = "XML Generate"

    module_path = fields.Char(string="Module Path", required=True)
    model_ids = fields.Many2many("ir.model", string="Models", required=True)

    def generate(self):
        self.ensure_one()

        for model in self.model_ids:
            # model_name: "education.course"
            model_name = model.model
            model_short = model_name.replace(".", "_")

            # Fields data
            fields_data = [
                {"name": f.name, "required": f.required}
                for f in model.field_id
                if f.store and not f.related
            ]

            # Load mako template
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

            # Output path: {module_path}/views/{model_short}_view.xml
            output_dir = os.path.join(self.module_path, "views")
            os.makedirs(output_dir, exist_ok=True)

            output_file = os.path.join(output_dir, f"{model_short}_view.xml")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(xml_content)

            print(f"XML generated: {output_file}")
