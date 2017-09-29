import bpy
import sys
import os
import re
import mathutils

# UBX_[RenderMeshName]_##
#  * Box collision mesh
# USP_[RenderMeshName]_##
#  * Sphere collision mesh
# UCX_[RenderMeshName]_##
#  * Convext collision mesh

class OT_dynamic_property(bpy.types.Operator):
    bl_idname = 'properties.mesh_export_status'
    bl_label = 'Export'
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        return {'FINISHED'}
    
class MeshExportPanel_select_all(bpy.types.Operator):
    bl_idname = "mesh_export_panel.select_all"
    bl_label = "Select All"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        for mesh in bpy.data.meshes:
            mesh.EX_export_this = True
            
        return {'FINISHED'}

class MeshExportPanel_select_none(bpy.types.Operator):
    bl_idname = "mesh_export_panel.select_none"
    bl_label = "Select None"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        for mesh in bpy.data.meshes:
            mesh.EX_export_this = False
            
        return {'FINISHED'}

class MeshExportPanel_export(bpy.types.Operator):
    bl_idname = "mesh_export_panel.export"
    bl_label = "Export"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        
        print (context.scene.engine_export_enum)
        
        # save selected objects
        selected_objects = context.selected_objects[:]
        
        # deselect selected objects
        for obj in context.selected_objects:
            obj.select = False
     
        # [:] copies the list.
        saved_layers = context.scene.layers[:]

        for object in bpy.context.scene.objects:
            if object.type == 'MESH' and not re.search(r'(UCX|USP|UCX)', object.name, re.M|re.I) and object.data.EX_export_this == True:
                object.select = True
                
                # turn on the object layer if it isn't on.
                object_layer = [i for i in range(len(object.layers)) if object.layers[i] == True]
                for i in range(len(bpy.context.scene.layers)):
                    if i in object_layer:
                        bpy.context.scene.layers[i] = True
                  
                # look for any UE4 collision mesh in children
                # FIXME: add numbering to mesh, ie: UCX_mesh_001, UCS_mesh_002, etc...
                if object.children:
                    for child in object.children:
                        if re.search(r'(UCX|USP|UBX)', child.name, re.M|re.I):
                            child.select = True
                                
                path = bpy.path.abspath(bpy.context.scene.conf_path + object.data.name + ".fbx")
                
                if context.scene.engine_export_enum == 'Unity':
                    bpy.ops.transform.rotate(value = -1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
                    bpy.ops.transform.rotate(value = -3.1416, axis = (0, 1, 0), constraint_axis = (False, True, False), constraint_orientation = 'GLOBAL')
                    bpy.ops.object.transform_apply(rotation = True)
                    print ("Exporting to Unity")
                
                elif context.scene.engine_export_enum == 'UE4':
                    #bpy.ops.transform.rotate(value = -1.5708, axis = (0, 0, 1), constraint_axis = (False, False, True), constraint_orientation = 'GLOBAL')
                    #bpy.ops.transform.rotate(value = -3.1416, axis = (0, 0, 1), constraint_axis = (False, False, True), constraint_orientation = 'GLOBAL')
                    #bpy.ops.object.transform_apply(rotation = True)
                    print ("Exporting to UE4")
            
                bpy.ops.export_scene.fbx(filepath=path,
                    use_default_take=False,
                    use_selection=True,
                    use_anim_action_all=False,
                    use_mesh_edges=True,
                    #bake_space_transform=True,
                    #axis_up="X",
                    #axis_forward="Z",
                    object_types={'MESH'})
                
                if context.scene.engine_export_enum == 'Unity':
                    bpy.ops.transform.rotate(value = 1.5708, axis = (1, 0, 0), constraint_axis = (True, False, False), constraint_orientation = 'GLOBAL')
                    bpy.ops.transform.rotate(value = 3.1416, axis = (0, 0, 1), constraint_axis = (False, False, True), constraint_orientation = 'GLOBAL')
                    bpy.ops.object.transform_apply(rotation = True)
                
                elif context.scene.engine_export_enum == 'UE4':
                    #bpy.ops.transform.rotate(value = 1.5708, axis = (0, 0, 1), constraint_axis = (False, False, True), constraint_orientation = 'GLOBAL')
                    #bpy.ops.transform.rotate(value = -3.1416, axis = (0, 0, 1), constraint_axis = (False, False, True), constraint_orientation = 'GLOBAL')
                    #bpy.ops.object.transform_apply(rotation = True)
                    print ("Exporting to UE4")
                    
            for foo in bpy.context.scene.objects:
                foo.select = False      

        # restore layers
        bpy.context.scene.layers = saved_layers
        
        # restore selected objects
        for obj in selected_objects:
            obj.select = True
        
        return {'FINISHED'}
 
class MeshExportPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Mesh Export"
    bl_idname = "OBJECT_PT_mesh_export_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        row = layout.row(align=True)
        row = layout.row(align=True)
        row.operator("mesh_export_panel.export")
        row = layout.row()
      
        #row.label(text=' Selected Actions:')

        row = layout.row()
        col = row.column()
        col.operator("mesh_export_panel.select_all")
        col = row.column()
        col.operator("mesh_export_panel.select_none")
       
        col = layout.column()
        col.prop(context.scene, 'conf_path')
         
        layout.prop(context.scene, "engine_export_enum", text="Engine: ")

        
        for object in bpy.context.scene.objects:
            if object.type != 'MESH':
                continue
       
            so = re.search(r'(UCX|USP|UBX)', object.name, re.M|re.I)
            if so:
                continue
            
            # consider indenting children
            row = layout.row(align=True)
            row.prop(object.data, "EX_export_this", text=object.data.name)

#def update_export_engine_enum(self, context):
#    context.scene.engine_export = self.engine_export_enum
    
def register():
    bpy.utils.register_class(MeshExportPanel)
    bpy.utils.register_class(MeshExportPanel_select_all)
    bpy.utils.register_class(MeshExportPanel_select_none)
    bpy.utils.register_class(MeshExportPanel_export)

    engines = [
        ("UE4","UE4", "UE4"),
        ("Unity", "Unity", "Unity"),  
    ]

    bpy.types.Scene.engine_export_enum = bpy.props.EnumProperty(items=engines)
  
    bpy.types.Scene.conf_path = bpy.props.StringProperty \
      (
      name = "Export Path",
      default = bpy.path.abspath("//Export\\FBX\\Mesh\\"),
      description = "Define the export path of your fbx files.",
      subtype = 'DIR_PATH'
      )
    
    
    bpy.utils.register_module(__name__)
   
      
      
    # add custom export flag property
    bpy.types.Mesh.EX_export_this = bpy.props.BoolProperty(default=False)
    
def unregister():
    del bpy.types.Scene.conf_path
    del bpy.types.Scene.export_engine_enum
    del bpy.types.Scene.export_engine
    
    return

#if __name__ == "__main__":
register()
