import maya.cmds as mc
import webbrowser

# =================================================================================
# ==  ↓↓↓  关于  ↓↓↓  ==
# =================================================================================
def create_about_section(parent_layout):
    """
    创建一个没有外边框的、简洁的“关于”UI区域。
    """
    # --- 信息 ---
    author_name = "橘猫不吃橘子皮"
    tool_version = "Maya(24)Final"
    github_link = "https://github.com/nihuiQAQma"
    
    about_column = mc.columnLayout(adjustableColumn=True, rowSpacing=5, parent=parent_layout)
    
    mc.text(label=f"{author_name}", align="center", font='boldLabelFont')
    mc.text(label=f"Version: {tool_version}", align="center")
    mc.separator(height=10, style='in')
    
    mc.button(label="Visit on GitHub", 
              command=lambda *args: webbrowser.open(github_link)
              )
              
    mc.setParent('..') 
    
    return about_column
# =================================================================================


# --- 主UI类 ---
class VertexSnapperUI:
    def __init__(self):
        self.window_id = "vertexSnapperUIWindow"
        # 内部变量名已根据正确逻辑调整
        self.reference_model = None  # 自动模式: 源模型 (提供位置)
        self.verts_to_move = []      # 手动模式: 目标顶点 (要移动)
        self.reference_verts = []    # 手动模式: 源顶点 (提供位置)

        if mc.window(self.window_id, exists=True):
            mc.deleteUI(self.window_id, window=True)
            
        self.create_ui()

    def create_ui(self):
        self.window = mc.window(self.window_id, title="顶点吸附", widthHeight=(350, 420), sizeable=True)
        
        main_form = mc.formLayout(parent=self.window)
        tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        
        # --- 标签页 1: 自动吸附 (使用你的标签，但逻辑正确) ---
        auto_snap_tab = mc.columnLayout(adjustableColumn=True, rowSpacing=10)
        mc.frameLayout(label="1. 设置源模型 (提供参考)", collapsable=False, marginHeight=10, marginWidth=5)
        mc.columnLayout(adjustableColumn=True)
        mc.button(label="使当前选择为源模型\nLoad Selected as Source", command=self.load_auto_source_model, height=40)
        self.auto_source_field = mc.textField(placeholderText="未加载源...", editable=False)
        mc.setParent('..'); mc.setParent('..')
        mc.separator(height=10, style='in')
        mc.frameLayout(label="2. 选择目标顶点并执行", collapsable=False, marginHeight=10, marginWidth=5)
        mc.columnLayout(adjustableColumn=True)
        mc.button(label="将选定顶点吸附到源位置\nSnap Selected Vertices to Source", command=self.execute_auto_snap, height=40, backgroundColor=(0.4, 0.6, 0.4))
        mc.setParent('..'); mc.setParent('..')
        mc.setParent(tabs)
        
        # --- 标签页 2: 手动吸附 (使用你的标签，但逻辑正确) ---
        manual_snap_tab = mc.columnLayout(adjustableColumn=True, rowSpacing=10)

        # Step 1: 加载源顶点 (提供位置)
        mc.frameLayout(label="Step 1: 加载源顶点    Load Source Vertices", collapsable=False, marginHeight=10, marginWidth=5)
        mc.rowLayout(numberOfColumns=2, columnWidth2=(250, 70))
        mc.button(label="源\nSource", command=self.load_manual_reference_verts, height=40)
        mc.button(label="Clear", command=self.clear_manual_reference_verts)
        mc.setParent('..')
        self.reference_vtx_field = mc.textField(placeholderText="没有顶点被加载...", editable=False)
        mc.setParent('..')
        
        # Step 2: 加载目标顶点 (要被移动)
        mc.frameLayout(label="Step 2: 加载目标顶点    Load Target Vertices", collapsable=False, marginHeight=10, marginWidth=5)
        mc.rowLayout(numberOfColumns=2, columnWidth2=(250, 70))
        mc.button(label="目标\nTarget", command=self.load_manual_verts_to_move, height=40)
        mc.button(label="Clear", command=self.clear_manual_verts_to_move)
        mc.setParent('..')
        self.verts_to_move_field = mc.textField(placeholderText="没有顶点被加载...", editable=False)
        mc.setParent('..')
        
        mc.separator(height=15, style='in')
        mc.button(label="Go Go Go", command=self.execute_manual_snap, height=40, backgroundColor=(0.4, 0.5, 0.65))
        mc.setParent(tabs)
        
        mc.tabLayout(tabs, edit=True, tabLabel=((auto_snap_tab, 'Auto Snap'), (manual_snap_tab, 'Manual Snap')))
        
        about_section = create_about_section(main_form)
        mc.formLayout(main_form, edit=True,
            attachForm=[(tabs, 'top', 5), (tabs, 'left', 5), (tabs, 'right', 5),
                        (about_section, 'left', 5), (about_section, 'right', 5), (about_section, 'bottom', 5)],
            attachControl=[(tabs, 'bottom', 5, about_section)])
        
        mc.showWindow(self.window)

    # --- 逻辑函数 (已根据正确定义调整) ---
    def load_auto_source_model(self, *args):
        selection = mc.ls(selection=True, type='transform', long=True)
        if not selection or len(selection) > 1: mc.warning("请只选择一个网格物体作为源模型。"); return
        source_model = selection[0]
        if not mc.listRelatives(source_model, shapes=True, type='mesh', path=True): mc.warning(f"'{source_model}' 不是一个有效的网格物体。"); return
        self.reference_model = source_model
        mc.textField(self.auto_source_field, edit=True, text=self.reference_model.split('|')[-1])

    def execute_auto_snap(self, *args):
        if not self.reference_model or not mc.objExists(self.reference_model): mc.warning("未设置源模型或源已删除。"); return
        target_verts = [v for v in mc.ls(selection=True, flatten=True, long=True) if '.vtx[' in v]
        if not target_verts: mc.warning("请选择要移动的目标顶点。"); return
        reference_positions = [mc.xform(v, query=True, translation=True, worldSpace=True) for v in mc.ls(f'{self.reference_model}.vtx[*]', flatten=True, long=True)]
        self._perform_snap_logic(target_verts, reference_positions)

    def load_manual_verts_to_move(self, *args):
        self.verts_to_move = [v for v in mc.ls(selection=True, flatten=True, long=True) if '.vtx[' in v]
        count = len(self.verts_to_move)
        mc.textField(self.verts_to_move_field, edit=True, text=f"{count} target vert(s) loaded.")

    def clear_manual_verts_to_move(self, *args):
        self.verts_to_move = []
        mc.textField(self.verts_to_move_field, edit=True, placeholderText="没有顶点被加载...")

    def load_manual_reference_verts(self, *args):
        self.reference_verts = [v for v in mc.ls(selection=True, flatten=True, long=True) if '.vtx[' in v]
        count = len(self.reference_verts)
        mc.textField(self.reference_vtx_field, edit=True, text=f"{count} source vert(s) loaded.")
        
    def clear_manual_reference_verts(self, *args):
        self.reference_verts = []
        mc.textField(self.reference_vtx_field, edit=True, placeholderText="没有顶点被加载...")
    
    def execute_manual_snap(self, *args):
        if not self.verts_to_move: mc.warning("未加载目标顶点，请先执行Step 2。"); return
        if not self.reference_verts: mc.warning("未加载源顶点，请先执行Step 1。"); return
        if not mc.objExists(self.verts_to_move[0]) or not mc.objExists(self.reference_verts[0]): mc.warning("源或目标物体已被删除，请重新加载。"); return
        reference_positions = [mc.xform(v, query=True, translation=True, worldSpace=True) for v in self.reference_verts]
        self._perform_snap_logic(self.verts_to_move, reference_positions)

    def _perform_snap_logic(self, verts_to_move, reference_positions):
        try:
            mc.undoInfo(openChunk=True)
            processed_count = 0
            for vtx_to_move in verts_to_move:
                if not mc.objExists(vtx_to_move): continue
                pos_to_move_from = mc.xform(vtx_to_move, query=True, translation=True, worldSpace=True)
                min_distance_squared, closest_ref_pos = float('inf'), None
                for ref_pos in reference_positions:
                    dist_sq = sum([(a - b)**2 for a, b in zip(pos_to_move_from, ref_pos)])
                    if dist_sq < min_distance_squared:
                        min_distance_squared = dist_sq
                        closest_ref_pos = ref_pos
                if closest_ref_pos:
                    mc.move(closest_ref_pos[0], closest_ref_pos[1], closest_ref_pos[2], vtx_to_move, worldSpace=True, absolute=True)
                    processed_count += 1
            if processed_count > 0: print(f"吸附成功！移动了 {processed_count} 个顶点。")
            else: mc.warning("未处理任何有效的顶点。")
        finally:
            mc.undoInfo(closeChunk=True)

# --- 运行UI ---
vertex_snapper_tool = VertexSnapperUI()