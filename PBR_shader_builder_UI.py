import os

TEXTURE_LIB_DIR_PATH = "D:/vfx/library/assets/textures/"
THIS_PROJECT = "build://project/"
SHDR_ROOT_CNTXT = THIS_PROJECT + "shading/"
WORKING_SHDR_CNTXT = ""
TEX_DIR = ""
MATERIALS_in_DIR = []
SCN_SHADERS = []
# TEX_CHANNELS = ["base_color", "roughness", "metallic"]
ALBEDO_VARIANTS = ["_diff_", "basecolor", "Base_Color", "albedo"]
NORMAL_VARIANTS = ["nor_GL", "nor_gl", "normal-ogl", "_normal", "_Normal"]
ROUGH_VARIANTS = ["Roughness", "roughness"]
METAL_VARIANTS = ["Metallic", "metallic"]
HEIGHT_VARIANTS = ["_disp_", "_height", "_Height", "-height"]
ARM_CHANNELS = ["roughness","metallic"]

SHADER_CONTEXT = ""
TEXTURE_CNTXT = ""
TEX_UTIL_CNTXT = ""
isArm = False
MATERIAL = ""
SHADER = ""


# this nugget was originally scripted by Anthony Nemoff and stolen by me with heartfelt thanks.
def get_or_create_ctx(ctx_name, parent_ctx_path):
    """
    Create the context only if it  doesn't exist yet and return it.
    ctx_name        : name (only) of the new context
    parent_ctx_path : full path (with trailing slash) of the parent context
    """
    full_path = parent_ctx_path + ctx_name
    if ix.item_exists(full_path) is None:
        # create it and return it
        return ix.cmds.CreateContext(ctx_name, "", parent_ctx_path)
    else:
        # already exists, return it
        return ix.get_item(full_path)

# this nugget was originally scripted by Anthony Nemoff and stolen by me with heartfelt thanks.
def find_objects_by_class(class_name):
    object_factory = ix.application.get_factory()
    assert object_factory.get_classes().exists(class_name), 'OfClass "{}" is unknown.'.format(class_name)

    root = object_factory.get_root()
    objects = ix.api.OfObjectArray()
    root.get_all_objects(class_name, objects)
    return objects

def createMapFile(shader, attribute):
    textureCtx = ix.get_current_context()
    if shader.is_kindof("Material"):
        texMapName = shader.get_name() + "_" + attribute + "_mapFile"
        texMapItem = ix.cmds.CreateObject(texMapName, "TextureMapFile", "Global", textureCtx.get_full_name())
        return texMapItem

def createNormalMapFiles(shader):
    attribute = "normal_input"
    textureCtx = ix.get_current_context()
    
    texNormMapFileName = shader.get_name() + "_" + attribute + "_mapFile"
    texNormMapName = shader.get_name() + "_" + attribute + "_Map"
    
    texNormMapFile = ix.cmds.CreateObject(texNormMapFileName, "TextureMapFile", "Global", textureCtx.get_full_name())
    texNormMap = ix.cmds.CreateObject(texNormMapName, "TextureNormalMap", "Global", textureCtx.get_full_name())
    normal_maps = [texNormMapFile, texNormMap]
    return normal_maps

def create_Set_Reorder(shader, attribute):
    reOrderName = shader.get_name() + "_" + attribute +  "_Reorder"
    textureCtx = ix.get_current_context()
    
    reorder = ix.cmds.CreateObject(reOrderName, "TextureReorder", "Global", textureCtx.get_full_name())
    if("roughness" in attribute):
        ix.cmds.SetValues([reorder.get_full_name() + ".channel_order[0]"], ["g"])
        return (reorder)
    elif("metallic" in attribute):
        ix.cmds.SetValues([reorder.get_full_name() + ".channel_order[0]"], ["b"])
        return (reorder)
    else:
        print("**WARNING!** : Attribute not supported yet.")

def deleteItem(itemFullName):
    ix.delete_item(itemFullName)
    print ("Deleted " + itemFullName)

def deleteExistingTexContext(shader):
    textureCtxName = shader.get_name() + "_texturesCTX"
    shaderCtx = shader.get_context()
    searchStr = shaderCtx.get_full_name() + "/" + textureCtxName
    if ix.item_exists(searchStr) is None:
        return False
    else:
        # already exists, return it
        deleteItem(searchStr)
        print ("deleted ctx")
        return True
 
def create_contextsTemplate(shader):
    shaderName = shader.get_name()
    shaderCtx = shader.get_context()
    SHDR_ROOT_CNTXT = ""
    textureCtxName = shader.get_name() + "_texturesCTX"
    texUtilCtxName = shader.get_name() + "_Util_texturesCTX"
    
    if deleteExistingTexContext(shader):
        shaderCtx = shader.get_context()
        shaderCtxChars = len(shaderCtx.get_name())
        fullSCtxpath = shaderCtx.get_full_name()
        ShRtpath = fullSCtxpath[0:-shaderCtxChars]
        SHDR_ROOT_CNTXT = ShRtpath
    else:
        shaderCtxName = shaderName + "_CTX"
        shaderCtx = shader.get_context()
        SHDR_ROOT_CNTXT = shaderCtx.get_full_name() + "/"
        shaderCtx = get_or_create_ctx(shaderCtxName, SHDR_ROOT_CNTXT)
        ix.cmds.MoveItemTo(shader.get_full_name() , shaderCtx.get_full_name())
            
    print ("LOG ::: " + shaderCtx.get_full_name())    
    
    textureCtx = get_or_create_ctx(textureCtxName, shaderCtx.get_full_name())
    texUtilCtx = get_or_create_ctx(texUtilCtxName, textureCtx.get_full_name())
    
    contexts = [shaderCtx, textureCtx, texUtilCtx, SHDR_ROOT_CNTXT]
   
    return contexts

def getShaderObj(shaderName):
    scn_shaders = find_objects_by_class('MaterialPhysical')
    
    for scn_shader in scn_shaders:
        if shaderName == scn_shader.get_name():
            return scn_shader

def createDisplacementMaps(shader):
    shaderCtx = shader.get_context()
    displacementName = shader.get_name() + "_displacement"
    searchStr = shaderCtx.get_full_name() + "/" + displacementName
    if ix.item_exists(searchStr) is None:
        print ("start creating NEW DISP MAP :::::::::::::")
        displacementMap = ix.cmds.CreateObject(displacementName, "Displacement", "Global", shaderCtx.get_full_name())
        displacementMapFile = createMapFile(shader, "displacement")
        ix.cmds.SetValues([displacementMapFile.get_full_name() +".use_raw_data"], ["1"])
        displacementMaps = [displacementMap, displacementMapFile]
        return displacementMaps
    else:
        print ("start extracting current DISP MAP :::::::::::::")
        currentDisplacementMap = ix.item_exists(searchStr)
        displacementMapFile = createMapFile(shader, "displacement")
        ix.cmds.SetValues([displacementMapFile.get_full_name() +".use_raw_data"], ["1"])
        ix.cmds.SetTexture([currentDisplacementMap.get_full_name() + ".front_value"], displacementMapFile.get_full_name())
        displacementMaps = [currentDisplacementMap, displacementMapFile]
        return displacementMaps
       
def create_triplanar(shader, attribute, force_planar):
    triplanarName = shader.get_name() + "_" + attribute + "_triplanar"
    textureCtx = ix.get_current_context()
    triplanar = ix.cmds.CreateObject(triplanarName, "TextureTriplanar", "Global", textureCtx.get_full_name())
    ix.cmds.SetValues([triplanar.get_full_name() + ".object_space"], ["2"])
    # ix.cmds.SetValues([triplanar.get_full_name() + ".blend"], [str(blend)])
    if force_planar:
        ix.cmds.SetValues([triplanar.get_full_name() + ".force_planar_projection"], ["True"])
    else:        
        ix.cmds.SetValues([triplanar.get_full_name() + ".force_planar_projection"], ["False"])
    return triplanar

def set_triplanarTo(shader, channelName, mapFile, triplanar):
    triplanarChannels = ["right","left","top","bottom","front","back"]
    for channel in triplanarChannels:
        ix.cmds.SetTexture([triplanar.get_full_name() + "." + channel], mapFile.get_full_name())
   
    ix.cmds.SetTexture([shader.get_full_name() + "." + channelName], triplanar.get_full_name())

def create_Set_Texture(channelName, shader, OSpath, isTriplanar, force_planar = False):
    
    if(channelName == "base_color"):
        albedoMapFile = createMapFile(shader, channelName)
        ix.cmds.SetValues([albedoMapFile.get_full_name() + ".filename[0]"], [OSpath])
        
        if(isTriplanar):
            triplanarMap = create_triplanar(shader, channelName, force_planar)
            set_triplanarTo(shader, channelName, albedoMapFile, triplanarMap)
            
        else:
            ix.cmds.SetTexture([shader.get_full_name() + ".base_color"], albedoMapFile.get_full_name())
        print("create and set texture mapFile for " + shader.get_name() + " Base color attribute.")

    elif(channelName == "roughness"):
        roughMapFile = createMapFile(shader, channelName)
        ix.cmds.SetValues([roughMapFile.get_full_name() + ".filename[0]"], [OSpath])
        ix.cmds.SetValues([roughMapFile.get_full_name() + ".use_raw_data"], ["1"])
        
        if(isTriplanar):
            triplanarMap = create_triplanar(shader, channelName, force_planar)
            set_triplanarTo(shader, channelName, roughMapFile, triplanarMap)
            
        else:
            ix.cmds.SetTexture([shader.get_full_name() + ".roughness"], roughMapFile.get_full_name())
        print("create and set texture mapFile for " + shader.get_name() + " roughness attribute.")
    
    elif(channelName == "metallic"):
        metalMapFile = createMapFile(shader, channelName)
        ix.cmds.SetValues([metalMapFile.get_full_name() + ".filename[0]"], [OSpath])
        ix.cmds.SetValues([metalMapFile.get_full_name() + ".use_raw_data"], ["1"])
        
        if(isTriplanar):
            triplanarMap = create_triplanar(shader, channelName, force_planar)
            set_triplanarTo(shader, channelName, metalMapFile, triplanarMap)
            
        else:
            ix.cmds.SetTexture([shader.get_full_name() + ".metallic"], metalMapFile.get_full_name())
        print("create and set texture mapFile for " + shader.get_name() + " metallic attribute.")
    
    elif(channelName == "arm"):
        armMapFile = createMapFile(shader, channelName)
        arm_attribs = ["roughness", "metallic"]
        
        ix.cmds.SetValues([armMapFile.get_full_name() + ".filename[0]"], [OSpath])
        ix.cmds.SetValues([armMapFile.get_full_name() + ".use_raw_data"], ["1"])
        # create reorder nodes
        reorder_rough = create_Set_Reorder(shader, arm_attribs[0])
        reorder_metal = create_Set_Reorder(shader, arm_attribs[1])
        #connect arm mapFile to reorder nodes
        ix.cmds.SetTexture([reorder_rough.get_full_name() + ".input"], armMapFile.get_full_name())
        ix.cmds.SetTexture([reorder_metal.get_full_name() + ".input"], armMapFile.get_full_name())
        
        if(isTriplanar):
            for attrib in arm_attribs:
                if "roughness" in attrib:
                    triplanarMap = create_triplanar(shader, attrib, force_planar)
                    set_triplanarTo(shader, attrib, reorder_rough, triplanarMap)
                if "metallic" in attrib:
                    triplanarMap = create_triplanar(shader, attrib, force_planar)
                    set_triplanarTo(shader, attrib, reorder_metal, triplanarMap)
            
        else:
            ix.cmds.SetTexture([shader.get_full_name() + "." + arm_attribs[0]], reorder_rough.get_full_name())
            ix.cmds.SetTexture([shader.get_full_name() + "." + arm_attribs[1]], reorder_metal.get_full_name())

    elif(channelName == "normal_input"):
        normalMaps = createNormalMapFiles(shader)
        
        normalMapPath = normalMaps[1].get_full_name()
        normalMapFilePath = normalMaps[0].get_full_name()
        ix.cmds.SetValues([normalMapFilePath + ".filename[0]"], [OSpath])
        ix.cmds.SetValues([normalMapFilePath + ".use_raw_data"], ["1"])
        ix.cmds.SetTexture([normalMapPath + ".input"], normalMapFilePath)
        
        if(isTriplanar):
            triplanarMap = create_triplanar(shader, channelName, force_planar)
            set_triplanarTo(shader, channelName, normalMaps[1], triplanarMap)
            
        else:
            ix.cmds.SetTexture([shader.get_full_name() + ".normal_input"], normalMapPath)

        print("create and set texture mapFile for " + shader.get_name() + " normal_input attribute.")
   
    elif(channelName == "displacement"):
        dispMaps = createDisplacementMaps(shader)
        ix.cmds.SetValues([dispMaps[1].get_full_name() + ".filename[0]"], [OSpath])
        
        if(isTriplanar):
            triplanarMap = create_triplanar(shader, channelName, force_planar)
            triplanarChannels = ["right","left","top","bottom","front","back"]
            for channel in triplanarChannels:
                ix.cmds.SetTexture([triplanarMap.get_full_name() + "." + channel], dispMaps[1].get_full_name())
   
            ix.cmds.SetTexture([dispMaps[0].get_full_name() + ".front_value"], triplanarMap.get_full_name())

        else:
            ix.cmds.SetTexture([dispMaps[0].get_full_name() + ".front_value"], dispMaps[1].get_full_name())
            print ("Nothing ")

        print("create and set texture mapFile for " + shader.get_name() + " displacement attribute.")
    
    elif(channelName == "emission_color"):
        print("TODO:create and set texture mapFile for " + shader.get_name() + " emission_color attribute.")
    elif(channelName == "emission_weight"):
        print("TODO:create and set texture mapFile for " + shader.get_name() + " emission_weight attribute.")
    elif(channelName == "opacity"):
        print("TODO:create and set texture mapFile for " + shader.get_name() + " Base color attribute.")

def createPBRTexMapFiles(materialName, shaderName, isTriplanar, force_planar):
    #def createPBRTexMapFiles (material, shader, shaderName)
    ix.begin_command_batch('create PBR texture SET')
    
    print ("Start create PBR Map Files")
    isArm = False
    # print (materialName +" // " + shaderName  + "   2")
    shader = getShaderObj(shaderName)
    
    WRK_contexts = create_contextsTemplate(shader)
    SHDR_ROOT_CNTXT = WRK_contexts[3]
    ix.set_current_context(WRK_contexts[1].get_full_name())
    
    TEX_DIR = TEXTURE_LIB_DIR_PATH + materialName + "/"
    TEX_FILES = os.listdir(TEX_DIR)
    
   ##ARM cbeck
    for TEX_FILE in TEX_FILES:
        # print("This is the name of the " + TEX_FILE + " found in TEX_DIR")
        if ("_arm_" in TEX_FILE):
            isArm = True
            print (TEX_FILE + " - isARM")

    # sort through textures and set color, arm, normal, rough, metal maps
    
    # ix.set_current_context(WRK_contexts[1].get_full_name())
    
    for TEX_FILE in TEX_FILES:
        TEX_PATH = TEX_DIR + TEX_FILE
        
        shader = getShaderObj(shaderName)
        
        for ALBEDO_VARIANT in ALBEDO_VARIANTS:
            if (ALBEDO_VARIANT in TEX_FILE and ".tx" not in TEX_FILE):
                ix.set_current_context(WRK_contexts[1].get_full_name())
                ATTR = "base_color"
                create_Set_Texture(ATTR, shader, TEX_PATH, isTriplanar, force_planar)
                break
                # print("Base color map found in " + TEX_PATH + ", and connected to " + shader.get_name() + "." + ATTR)
   
        for NORMAL_VARIANT in NORMAL_VARIANTS:
            if (NORMAL_VARIANT in TEX_FILE and ".tx" not in TEX_FILE):
                ix.set_current_context(WRK_contexts[2].get_full_name())
                ATTR = "normal_input"
                create_Set_Texture(ATTR, shader, TEX_PATH, isTriplanar, force_planar)
                break
                # print("Normal map found in " + TEX_PATH + ", and connected to " + shader.get_name() + "." + ATTR)

        for ROUGH_VARIANT in ROUGH_VARIANTS:
            if (ROUGH_VARIANT in TEX_FILE and ".tx" not in TEX_FILE):
                ix.set_current_context(WRK_contexts[1].get_full_name())
                ATTR = "roughness"
                create_Set_Texture(ATTR, shader, TEX_PATH, isTriplanar, force_planar)   
                break                
       
        for METAL_VARIANT in METAL_VARIANTS:
            if (METAL_VARIANT in TEX_FILE and ".tx" not in TEX_FILE):
                ix.set_current_context(WRK_contexts[1].get_full_name())
                ATTR = "metallic"
                create_Set_Texture(ATTR, shader, TEX_PATH, isTriplanar, force_planar)
                break
                # print("metal map found in " + TEX_PATH)
        
        for HEIGHT_VARIANT in HEIGHT_VARIANTS:
            if (HEIGHT_VARIANT in TEX_FILE and ".tx" not in TEX_FILE):
                ix.set_current_context(WRK_contexts[1].get_full_name())
                ATTR = "displacement"
                create_Set_Texture(ATTR, shader, TEX_PATH, isTriplanar, force_planar)
                break
                
    for TEX_FILE in TEX_FILES:
        TEX_PATH = TEX_DIR + TEX_FILE
        
        shaderFullName = SHDR_ROOT_CNTXT + shaderName
        shader = getShaderObj(shaderName) 
            
        if(isArm):
            if ("_arm_" in TEX_FILE and ".tx" not in TEX_FILE):
               
                ix.set_current_context(WRK_contexts[2].get_full_name())
                ATTR = "arm"
                create_Set_Texture(ATTR, shader, TEX_PATH, isTriplanar, force_planar)
                break
              #  print("ARM map found in " + TEX_PATH + ", and connected to " + shader + "." + ATTR)
            
                    # print("Roughness map found in " + TEX_PATH)
    ix.set_current_context(WRK_contexts[0].get_full_name())
    
    ix.end_command_batch()



class EventRewire(ix.api.EventObject):
    #These are the called functions by the connect. It is more flexible to make a function for each button
    MAT = ""
    SHAD = ""
    isTriplanar = False
    force_planar = False
    def materialListRefresh(self, sender, evtid):
       # print("Selected " + sender.get_selected_item_name())
        self.MAT = sender.get_selected_item_name()
        print("Selected " + self.MAT)

    def shaderListRefresh(self, sender, evtid):
        #print("Selected " + sender.get_selected_item_name())
        self.SHAD = sender.get_selected_item_name()
        print("Selected " + self.SHAD)

    def TriPcheckBoxRefresh(self, sender, evtid):
        self.isTriplanar = sender.get_value() #refresh result
    
    def FPcheckBoxRefresh(self, sender, evtid):
        self.force_planar = sender.get_value() #refresh result
 
    def assign_texture_set(self, sender, evtid):
        #Put here the core of your script (or a function to separate UI and Script)
        print (self.MAT)
        print (self.SHAD)
        # print (str(self.isTriplanar))
        createPBRTexMapFiles(self.MAT, self.SHAD, self.isTriplanar, self.force_planar) 
# -----------------------------------------------------------------------------------------------

MATERIALS_in_DIR = os.listdir(TEXTURE_LIB_DIR_PATH)
SCN_SHADERS = find_objects_by_class('MaterialPhysical')

# -----------------------------------------------------------------------------------------------
#Window creation

clarisse_win = ix.application.get_event_window()
my_window = ix.api.GuiWindow(clarisse_win, 1600, 400, 400, 250)
my_window.set_title('Assign Existing Texture Set')

    #Main widget creation
panel = ix.api.GuiPanel(my_window, 0, 0, my_window.get_width(), my_window.get_height())
panel.set_constraints(ix.api.GuiWidget.CONSTRAINT_LEFT, ix.api.GuiWidget.CONSTRAINT_TOP, ix.api.GuiWidget.CONSTRAINT_RIGHT, ix.api.GuiWidget.CONSTRAINT_BOTTOM)

       
separator_label2 = ix.api.GuiLabel(panel, 20, 10, 220, 25, "Select Shader")
separator_label2.set_text_color(ix.api.GMathVec3uc(255, 150, 150))
        # Select shader Label

list_button_shaders = ix.api.GuiListButton(panel,20, 35,350,30)
for i in range(len(SCN_SHADERS)):
    isSelected = True if i == 0 else False
    list_button_shaders.add_item(SCN_SHADERS[i].get_name(), isSelected)

 # Select material Label
separator_label1 = ix.api.GuiLabel(panel, 20, 70, 220, 25, "Select Material")
separator_label1.set_text_color(ix.api.GMathVec3uc(255, 50, 50))

        # Material list dropdown
list_button_materials = ix.api.GuiListButton(panel, 20, 100, 350, 30)
for i, matName in enumerate(MATERIALS_in_DIR):
    isSelected = True if i == 0 else False
    list_button_materials.add_item(matName, isSelected)

TriPcheckBoxLabel  = ix.api.GuiLabel(panel, 20, 140, 70, 22, "is TriPlanar") #Clarrisse_function(parent, X_position, Y_position, Width, Height, "label")
TriPcheckBox = ix.api.GuiCheckbox(panel, 90, 140, "")

FPcheckBoxLabel  = ix.api.GuiLabel(panel, 120, 140, 150, 22, "Force Planar Projection") #Clarrisse_function(parent, X_position, Y_position, Width, Height, "label")
FPcheckBox = ix.api.GuiCheckbox(panel, 250, 140, "")

apply_button = ix.api.GuiPushButton(panel, 300, 140, 60, 40, "Apply")

event_rewire = EventRewire() #init the class

event_rewire.connect(list_button_materials, 'EVT_ID_LIST_BUTTON_SELECT', event_rewire.materialListRefresh) #connect(item_to_listen, what_we_are_listening, function_called)
event_rewire.connect(list_button_materials, 'EVT_ID_LIST_BUTTON_SELECT_UNCHANGED', event_rewire.materialListRefresh) #connect(item_to_listen, what_we_are_listening, function_called)
event_rewire.connect(list_button_shaders, 'EVT_ID_LIST_BUTTON_SELECT', event_rewire.shaderListRefresh) #connect(item_to_listen, what_we_are_listening, function_called)
event_rewire.connect(list_button_shaders, 'EVT_ID_LIST_BUTTON_SELECT_UNCHANGED', event_rewire.shaderListRefresh) #connect(item_to_listen, what_we_are_listening, function_called)
event_rewire.connect(TriPcheckBox, 'EVT_ID_CHECKBOX_CLICK', event_rewire.TriPcheckBoxRefresh) #connect(item_to_listen, what_we_are_listening, function_called)
event_rewire.connect(apply_button, 'EVT_ID_PUSH_BUTTON_CLICK', event_rewire.assign_texture_set) #connect(item_to_listen, what_we_are_listening, function_called)



#generate the <span class="posthilit">gui</span>
my_window.show()
while my_window.is_shown():
    ix.application.check_for_events()
my_window.destroy()