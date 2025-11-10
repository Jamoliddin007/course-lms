from odoo import models, fields

class XMLGenerateWizard(models.TransientModel):
    _name = "xml.generate.wizard"
    _description = "XML Generate Wizard"

    module_path = fields.Char(string="Module Path", required=True)
    model_ids = fields.Many2many("ir.model", string="Models", required=True)

    def action_generate_xml(self):
        self.ensure_one()
        xml_generator = self.env["xml.generate"].create({
            "module_path": self.module_path,
            "model_ids": [(6, 0, self.model_ids.ids)],
        })
        xml_generator.generate()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "XML Generation Complete",
                "message": "XML files have been successfully generated.",
                "sticky": False,
            },
        }
