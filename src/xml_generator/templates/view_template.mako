<odoo>
    <record id="view_${model_short}_list" model="ir.ui.view">
        <field name="name">${model_short}.list</field>
        <field name="model">${model_name}</field>
        <field name="arch" type="xml">
            <list string="${model_name.split('.')[-1].capitalize()}">
                % for field in fields:
                <field name="${field['name']}"/>
                % endfor
            </list>
        </field>
    </record>

    <record id="view_${model_short}_form" model="ir.ui.view">
        <field name="name">${model_short}.form</field>
        <field name="model">${model_name}</field>
        <field name="arch" type="xml">
            <form string="${model_name.split('.')[-1].capitalize()}">
                <sheet>
                    <group>
                        % for field in fields:
                        <field name="${field['name']}"/>
                        % endfor
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_${model_short}" model="ir.actions.act_window">
        <field name="name">${model_name.split('.')[-1].capitalize()}</field>
        <field name="res_model">${model_name}</field>
        <field name="view_mode">list,form</field>
    </record>

    <menuitem id="menu_${model_short}" name="${model_name.split('.')[-1].capitalize()}" action="action_${model_short}"/>
</odoo>
