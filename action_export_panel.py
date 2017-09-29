import bpy
import sys
import os

class OT_dynamic_property(bpy.types.Operator):
    bl_idname = 'properties.action_export_status'
    bl_label = 'Export'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        return {'FINISHED'}
    
class ActionExportPanel_select_all(bpy.types.Operator):
    bl_idname = "action_export_panel.select_all"
    bl_label = "Select All"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        for action in bpy.data.actions:
            action.EX_export_this = True
            
        return {'FINISHED'}

class ActionExportPanel_select_none(bpy.types.Operator):
    bl_idname = "action_export_panel.select_none"
    bl_label = "Select None"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        for action in bpy.data.actions:
            action.EX_export_this = False
            
        return {'FINISHED'}

class ActionExportPanel_export(bpy.types.Operator):
    bl_idname = "action_export_panel.export"
    bl_label = "Export"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        start_action = context.object.animation_data.action
        
        for action in bpy.data.actions:
            if action.EX_export_this == True:
                context.object.animation_data.action = action
                path = bpy.path.abspath("//Export\\FBX\\Action\\" + action.name + ".fbx")
                bpy.ops.export_scene.fbx(filepath=path,
                    use_default_take=False,
                    use_selection=True,
                    use_anim_action_all=False,
                    use_mesh_edges=True,
                    object_types={'MESH','ARMATURE'})
        
        context.object.animation_data.action = start_action
        
        return {'FINISHED'}
 
class ActionExportPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Action Export"
    bl_idname = "OBJECT_PT_export_action_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        row = layout.row(align=True)
        row.operator("action_export_panel.export")
        row = layout.row()
        
        #row.label(text=' Selected Actions:')
       
        row = layout.row()
        col = row.column()
        col.operator("action_export_panel.select_all")
        col = row.column()
        col.operator("action_export_panel.select_none")
        
        for action in bpy.data.actions:
           row = layout.row(align=True)
           row.prop(action, "EX_export_this", text=action.name)

def register():
    bpy.utils.register_class(ActionExportPanel)
    bpy.utils.register_class(ActionExportPanel_select_all)
    bpy.utils.register_class(ActionExportPanel_select_none)
    bpy.utils.register_class(ActionExportPanel_export)
    
    bpy.types.Action.EX_export_this = bpy.props.BoolProperty(default=False)
    
def unregister():
   return

#if __name__ == "__main__":
register()
