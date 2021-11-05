import sys
import os
from ToothPaint_CV import*
from ToothPaint_UI import*

CV = Paint_CV()

class Paint(QMainWindow):
    def __init__(self):
        self.new = True
        self.selection = False
        self.Move = False
        self.toolSelected = 0
        self.complete_selection = False
        self.init_coords = []
        self.color = (0,0,0)
        self.color_bg = (255,255,255)
        self.color_backdrop = None
        self.color_backdrop_2 = None
        self.thickness = 1
        self.point = False
        self.zoom = [1,1]
        self.Aspc_ratio = True
        self.resize_value=[100,100,0,0]
        self.grid = 0
        self.font = [0, 1.0]
        self.filtered = False
        self.collection = []
        self.filterINDEX = 0
        self.image_BACKDROP = [None, None]
        self.image_SPLIT = [None, None]
        super(Paint,self).__init__()
        self.UI = WidgetUI(self)
        self.resize(1225, 770)
        self.setWindowIcon(QIcon("TP_assets/icon.png"))
        self.setWindowTitle("TOOTH PAINT by Low Jun Hong BS18110173")
        self.UI.SplashScreen()
        self.initUI()

    def closeEvent(self, event):
        event.ignore()
        self.UI.QuitDialog(sys)

    def initUI(self):
        tracker = MouseTracker(self.UI.canvas)
        tracker.positionChanged.connect(self.DetectPOS)
        self.zoom_slider = self.UI.SliderWidget(Qt.Horizontal, 100, 1, 500, 150, lambda :self.zoomTool(1))
        self.zoom_percentage = self.UI.Label_TextOnly("\t100%", ('Calibri', 10))
        plus_btn = self.UI.PushBtnIcon("TP_assets/plus.png", lambda :self.zoomTool(2))
        minus_btn = self.UI.PushBtnIcon("TP_assets/minus.png", lambda :self.zoomTool(3))
        self.pixel_dim = self.UI.Label_TextOnly("Dimension :      -      ", ('Calibri', 10))
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.UI.canvas)
        self.setCentralWidget(self.scrollArea)
        self.dockProperties = self.Dock_Details(True)
        self.dockPreview = self.Dock_Details(False)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockProperties)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dockPreview)
        self.statusBar()
        self.UI.StatusBAR(self.statusBar(), [None, self.pixel_dim, None, self.zoom_percentage, minus_btn, self.zoom_slider, plus_btn])
        self.Menubars()
        self.Toolbars()
        self.TextEdit = QLineEdit(self)
        self.TextEdit.setText("Please Enter Here")
        self.TextEdit.textChanged.connect(self.UpdateText)
        self.TextEdit.hide()

    def DetectPOS(self, pos):
        if 1<=self.toolSelected<=7:
            if self.toolSelected == 1 and self.complete_selection:
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.cursorINregion((mouse_x, mouse_y)):
                    self.UI.canvas.setCursor(QCursor(Qt.SizeAllCursor))
                else:
                    self.UI.canvas.setCursor(QCursor(Qt.CrossCursor))
            else:
                self.UI.canvas.setCursor(QCursor(Qt.CrossCursor))
        elif self.toolSelected==8 and not self.point:
            self.UI.canvas.setCursor(QCursor(Qt.IBeamCursor))
        elif self.toolSelected==9:
            self.UI.canvas.setCursor(QCursor(Qt.ClosedHandCursor))
        elif self.toolSelected==10:
            self.UI.canvas.setCursor(QCursor(Qt.PointingHandCursor))
        self.statusBar().showMessage(str(pos.x()) + ", " + str(pos.y()) + "px")

    def keyPressEvent(self, event):
        if self.toolSelected==1 and self.complete_selection and event.key()==Qt.Key_Delete:     #Delete selected image
            self.selection = self.Move = self.complete_selection = self.manual_selection = False
            image = self.image_backup.copy()
            image = np.zeros((image.shape[0], image.shape[1], 3), np.uint8)
            image[:] = self.color_bg
            self.image = CV.OverlayImage(image, self.image, self.toolCoords)
            self.image_CVT = CV.OverlayImage(image, self.image_CVT, self.toolCoords)
            self.Render(self.image)
        elif self.toolSelected==8 and self.point:
            if event.key()==Qt.Key_Escape:
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.point = False
                self.TextEdit.hide()
                self.Render(self.image)

    def mousePressEvent(self, event):
        if self.toolSelected!=0:
            if event.button()==1:
                pos = self.UI.canvas.mapFromGlobal(self.mapToGlobal(event.pos()))
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.toolSelected==1:
                    if not self.selection:
                        self.image_backup = self.image.copy()  # creating image backup
                        self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale
                        self.init_coords = (mouse_x, mouse_y)
                        self.selection = True
                    else:
                        if self.cursorINregion((mouse_x, mouse_y)):
                            self.Move = True
                            LR, UD, dst = CV.calcRegion((mouse_x, mouse_y, self.toolCoords[0], self.toolCoords[1]))
                            self.init_coords = (dst[0] * LR, dst[1] * UD)       # distance parameter instead of fixed point #moving de coord
                        else:
                            self.selection = self.Move = self.complete_selection = self.manual_selection = False
                            self.image = CV.OverlayImage(self.image_backup.copy(), self.image, self.toolCoords)
                            self.image_CVT = CV.OverlayImage(self.image_CVT_backup.copy(), self.image_CVT, self.toolCoords)
                            self.Render(self.image)
                elif self.toolSelected == 2 or self.toolSelected == 9:
                    self.init_coords = (mouse_x, mouse_y)
                elif 3<=self.toolSelected<= 7:
                    self.image_backup = self.image.copy()           # creating image backup
                    self.image_CVT_backup = self.image_CVT.copy()   # creating image backup for GrayScale
                    self.init_coords = (mouse_x, mouse_y)
                elif self.toolSelected==8:
                    if not self.point:
                        self.image_backup = self.image.copy()  # creating image backup
                        self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale
                        self.init_coords = (mouse_x, mouse_y)
                        self.point = True
                        self.TextEdit.move(self.init_coords[0], self.init_coords[1])
                        self.TextEdit.setText("Please Enter Here")
                        self.TextEdit.show()
                        self.UpdateText()
                    else:
                        self.point = False
                        CV.drawText(self.image, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
                        CV.drawText(self.image_CVT, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
                        self.TextEdit.hide()
                elif self.toolSelected == 10:
                    color = self.image[mouse_y, mouse_x]
                    self.color = (int(color[0]),int(color[1]), int(color[2]))
                    self.colorBtn.setIcon(QIcon(self.setPixmap_QtImg(CV.Color_picker(self.color), 45,45, False)))

    def mouseReleaseEvent(self, event):
        if self.toolSelected != 0:
            if event.button()==1:
                pos = self.UI.canvas.mapFromGlobal(self.mapToGlobal(event.pos()))
                mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
                if self.toolSelected==1:
                    if self.selection:
                        if not self.Move and not self.complete_selection:
                            self.toolCoords = CV.ReLocateCoords([self.init_coords[0], self.init_coords[1], mouse_x, mouse_y])
                            image = self.image_backup.copy()
                            CV.drawPrimitive(image, self.toolCoords, 1, None, int(2/max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp
                            self.Render(image)
                            self.image_backup = CV.CropImage(self.image.copy(), self.toolCoords)
                            self.image_CVT_backup = CV.CropImage(self.image_CVT.copy(), self.toolCoords)
                            CV.drawPrimitive(self.image, self.toolCoords, 5, (255, 255, 255), -1)       # make empty to selected region on base image
                            self.image_backup2 = self.image.copy()
                            CV.drawPrimitive(self.image_CVT, self.toolCoords, 5, (255, 255, 255), -1)  # make empty to selected region on base image
                            self.complete_selection = self.manual_selection = True
                        else:   #moving cropped image
                            self.Move = False
                elif 3 <= self.toolSelected <= 7:
                    if self.thickness == -1 and 6 <= self.toolSelected <= 7:
                        CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected + 2, self.color)
                        CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected + 2, self.color)
                    else:
                        CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
                        CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
                    self.Render(self.image)
                    self.image_backup = self.image.copy()  # creating image backup
                    self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale

    def mouseMoveEvent(self, event):
        pos = self.UI.canvas.mapFromGlobal(self.mapToGlobal(event.pos()))
        mouse_x, mouse_y = int(pos.x() / self.zoom[0]), int(pos.y() / self.zoom[1])
        if self.toolSelected==1:
            if self.selection:
                image = self.image_backup.copy()
                if not self.Move and not self.complete_selection:
                    CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 1, None, int(1/max(self.zoom[0], self.zoom[1])))  # only using backup image to render since temp
                    self.Render(image)
                else:
                    self.moveImage((mouse_x, mouse_y), image)
        elif self.toolSelected==2:
            CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color, self.thickness)
            CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color, self.thickness)
            self.init_coords = (mouse_x, mouse_y)
            self.Render(self.image)
        elif 3<=self.toolSelected<=7:
            image = self.image_backup.copy()
            if self.thickness==-1 and 6<=self.toolSelected<=7:
                CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected+2, self.color)
            else:
                CV.drawPrimitive(image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), self.toolSelected, self.color, self.thickness)
            self.Render(image)
        elif self.toolSelected==9:
            width = abs(self.thickness*2)
            CV.drawPrimitive(self.image, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color_bg, width)
            CV.drawPrimitive(self.image_CVT, (self.init_coords[0], self.init_coords[1], mouse_x, mouse_y), 3, self.color_bg, width)
            self.init_coords = (mouse_x, mouse_y)
            self.Render(self.image)
            self.image_backup = self.image.copy()  # creating image backup
            self.image_CVT_backup = self.image_CVT.copy()  # creating image backup for GrayScale

    def cursorINregion(self, mousepos):
        inregion = False
        if self.toolCoords[2] < self.toolCoords[0]:
            if self.toolCoords[2] <= mousepos[0]<=self.toolCoords[0]:
                inregion = True
        elif self.toolCoords[2] > self.toolCoords[0]:
            if self.toolCoords[0] <= mousepos[0] <= self.toolCoords[2]:
                inregion = True
        if inregion:
            inregion = False
            if self.toolCoords[3] < self.toolCoords[1]:
                if self.toolCoords[3] <= mousepos[1]<=self.toolCoords[1]:
                    inregion = True
            elif self.toolCoords[3] > self.toolCoords[1]:
                if self.toolCoords[1] <= mousepos[1] <= self.toolCoords[3]:
                    inregion = True
        return inregion

    def sharpenKernelUPDATE(self):
        value = self.spinSharpenKernel.value() * self.spinSharpenKernel.value()
        self.spinSharpenLevel.setMinimum(value)
        self.spinSharpenLevel.setValue(value)

    def ROWCOL_update(self, flag):
        spinRow = spinCol = currentROWCOL = table = None
        if flag == 1:
            spinRow, spinCol = self.spinROW.value(), self.spinCOL.value()
            currentROWCOL = self.currentROWCOL
            table = self.customTable
        elif flag == 2:
            spinRow, spinCol = self.spinMergeROW.value(), self.spinMergeCOL.value()
            currentROWCOL = self.currentMRC
            table = self.mergeTABLE
        elif flag == 3:  # flag 3
            spinRow, spinCol = self.spinSplitROW.value(), self.spinSplitCOL.value()
            currentROWCOL = self.currentSRC
            table = self.splitTABLE
        elif flag == 4:
            spinRow, spinCol = self.ColorSeg_count, 2
            currentROWCOL = self.currentSegRC
            table = self.segCOLTABLE
        elif flag == 5:
            spinRow, spinCol = self.spinKMCluster.value(), 3
            currentROWCOL = self.currentKMClst
            table = self.KM_clstTABLE
        elif flag == 6:
            if self.reduceSeg<self.spinSLIC_Seg.value():
                ROW = self.reduceSeg
            else:
                ROW = self.spinSLIC_Seg.value()
            spinRow, spinCol = ROW, 4
            currentROWCOL = self.currentSLIC
            table = self.SLIC_TABLE
        elif flag == 7:
            spinRow, spinCol = self.THCluster_len, 4
            currentROWCOL = self.currentTHClst
            table = self.TH_clstTABLE
        if spinRow > currentROWCOL[0]:
            while table.rowCount()<spinRow:
                table.insertRow(table.rowCount())
                if flag == 1:
                    for col in range(spinCol):
                        item = QTableWidgetItem("0")
                        item.setTextAlignment(Qt.AlignCenter)
                        table.setItem(table.rowCount() - 1, col, item)
                elif flag == 4:
                    spin = []
                    lbl1 = self.UI.CanvasLabel(True, True, Qt.AlignCenter)
                    lbl1.setPixmap(self.setPixmap_QtImg(CV.Color_picker((0, 0, 0), (0, 0), hsv=True), 142, 15, False))
                    lbl2 = self.UI.CanvasLabel(True, True, Qt.AlignCenter)
                    lbl2.setPixmap(self.setPixmap_QtImg(CV.Color_picker((0, 0, 0), (0, 0), hsv=True), 142, 15, False))
                    self.ColorSeg_label.append((lbl1, lbl2))
                    for col in range(6):
                        if col == 0 or col == 3:
                            maxVal = 180
                        else:
                            maxVal = 255
                        spin.append(self.UI.SpinBox(True, 0, maxVal, 0, action=lambda _, shape=(table.rowCount() - 1, col): self.Seg_COL_ORI(1, shape), width=45))
                    self.ColorSeg_spin.append(spin)
                    for col in range(spinCol):
                        hh = QHBoxLayout()
                        vv = QVBoxLayout()
                        qq = QWidget()
                        vv.addWidget(self.ColorSeg_label[table.rowCount() - 1][col])
                        if col == 0:
                            for i in range(3):
                                hh.addWidget(self.ColorSeg_spin[table.rowCount() - 1][i])
                        else:
                            for i in range(3, 6):
                                hh.addWidget(self.ColorSeg_spin[table.rowCount() - 1][i])
                        vv.addLayout(hh)
                        qq.setLayout(vv)
                        table.setCellWidget(table.rowCount() - 1, col, qq)
                elif 5<=flag<=7:
                    func_flag = flag-3
                    item = QTableWidgetItem(str(table.rowCount()))
                    item.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
                    item.setTextAlignment(Qt.AlignCenter)
                    table.setItem(table.rowCount() - 1, 0, item)
                    col_btn = self.UI.PushBtnIcon("TP_assets/dropper.png", action=lambda _, shape=(table.rowCount() - 1, 0): self.Seg_COL_ORI(func_flag, shape), iconSize=(25,25))
                    ori_check = self.UI.CheckBOX(None, lambda _, shape=(table.rowCount() - 1, 1): self.Seg_COL_ORI(func_flag, shape), True)
                    ori_lay = QHBoxLayout()
                    ori_lay.addStretch(1)
                    ori_lay.addWidget(ori_check)
                    ori_lay.addStretch(1)
                    oriori = QWidget()
                    oriori.setLayout(ori_lay)
                    table.setCellWidget(table.rowCount() - 1, 1, col_btn)
                    table.setCellWidget(table.rowCount() - 1, 2, oriori)
                    if flag == 5:
                        self.KMClst_btn.append((col_btn, ori_check))
                        self.KMClst_COL.append(None)
                    elif flag==6:
                        mask_check = self.UI.CheckBOX(None, lambda _, shape=(table.rowCount() - 1, 2): self.Seg_COL_ORI(func_flag, shape), True)
                        mask_lay = QHBoxLayout()
                        mask_lay.addStretch(1)
                        mask_lay.addWidget(mask_check)
                        mask_lay.addStretch(1)
                        maskmask = QWidget()
                        maskmask.setLayout(mask_lay)
                        table.setCellWidget(table.rowCount() - 1, 3, maskmask)
                        self.SLIC_btn.append((col_btn, ori_check, mask_check))
                        self.SLIC_COL.append(None)
                        self.SLIC_mask.append(True)
                    elif flag == 7:
                        mask_check = self.UI.CheckBOX(None, lambda _, shape=(table.rowCount() - 1, 2): self.Seg_COL_ORI(func_flag, shape), True)
                        mask_lay = QHBoxLayout()
                        mask_lay.addStretch(1)
                        mask_lay.addWidget(mask_check)
                        mask_lay.addStretch(1)
                        maskmask = QWidget()
                        maskmask.setLayout(mask_lay)
                        table.setCellWidget(table.rowCount() - 1, 3, maskmask)
                        self.THClst_btn.append((col_btn, ori_check, mask_check))
                        self.THClst_COL.append(None)
                        self.TH_mask.append(True)
        elif currentROWCOL[0] > spinRow:
            while table.rowCount()>spinRow:
                table.removeRow(table.rowCount() - 1)
                if flag == 4:
                    self.ColorSeg_spin.pop()
                    self.ColorSeg_label.pop()
                elif flag == 5:
                    self.KMClst_btn.pop()
                    self.KMClst_COL.pop()
                elif flag == 6:
                    self.SLIC_btn.pop()
                    self.SLIC_COL.pop()
                elif flag == 7:
                    self.THClst_btn.pop()
                    self.THClst_COL.pop()
        if spinCol > currentROWCOL[1]:
            while table.columnCount() < spinCol:
                table.insertColumn(table.columnCount())
                if flag == 1:
                    for row in range(spinRow):
                        table.setItem(row, table.columnCount() - 1, QTableWidgetItem("0"))
        elif currentROWCOL[1] > spinCol:
            while table.columnCount() > spinCol:
                table.removeColumn(table.columnCount() - 1)
        if flag == 1:
            self.currentROWCOL = [spinRow, spinCol]
        else:
            if flag == 2:
                self.mergeINDbtn = []
            elif flag == 3:
                self.splitINDbtn = []
            for row in range(spinRow):
                buttons = []
                for col in range(spinCol):
                    if flag == 2:
                        buttons.append([self.UI.PushBtnIcon("TP_assets/plus.png", lambda _, shape=(row, col): self.viewAvailableImage(shape), True), None, None])
                    elif flag == 3:
                        buttons.append(self.UI.PushBtnIcon("TP_assets/split.png", lambda _, shape=(row, col): self.collectionDialog(shape), True, iconSize=(25,25), enable=False))
                if flag == 2:
                    self.mergeINDbtn.append(buttons)
                elif flag == 3:
                    self.splitINDbtn.append(buttons)
            for row in range(spinRow):
                for col in range(spinCol):
                    if flag == 2:
                        table.setCellWidget(row, col, self.mergeINDbtn[row][col][0])
                    elif flag == 3:
                        table.setCellWidget(row, col, self.splitINDbtn[row][col])
            if flag == 2:
                self.currentMRC = [spinRow, spinCol]
            elif flag == 3:
                self.currentSRC = [spinRow, spinCol]
            elif flag ==4:
                self.currentSegRC = [spinRow, spinCol]
            elif flag ==5:
                self.currentKMClst = [spinRow, spinCol]
                self.FilterFunc(self.filterINDEX)
            elif flag ==6:
                self.currentSLIC = [spinRow, spinCol]
                self.FilterFunc(self.filterINDEX)
            elif flag ==7:
                self.currentTHClst = [spinRow, spinCol]
                # self.FilterFunc(self.filterINDEX)

    def Dock_Details(self, flag):
        dock_container = QWidget()
        dock_container_layout = QVBoxLayout()
        if flag:
            self.taby = QTabWidget()
            tab_HIST = QWidget()
            tab_FILTER = QScrollArea()
            tab_EDGE = QScrollArea()
            tab_MERGE = QScrollArea()
            tab_SPLIT = QScrollArea()
            tab_SEG = QScrollArea()
            self.taby.addTab(tab_HIST, "Histogram")
            self.taby.addTab(tab_FILTER, "Filter")
            self.taby.addTab(tab_EDGE, "Edge")
            self.taby.addTab(tab_MERGE, "Merge")
            self.taby.addTab(tab_SPLIT, "Split")
            self.taby.addTab(tab_SEG, "Segmentation")
            content_FILTER = QWidget()
            tab_FILTER.setWidget(content_FILTER)
            FilterLay = QVBoxLayout(content_FILTER)
            tab_FILTER.setWidgetResizable(True)
            content_EDGE = QWidget()
            tab_EDGE.setWidget(content_EDGE)
            EdgeLay = QVBoxLayout(content_EDGE)
            tab_EDGE.setWidgetResizable(True)
            content_MERGE = QWidget()
            tab_MERGE.setWidget(content_MERGE)
            MergeLay = QVBoxLayout(content_MERGE)
            tab_MERGE.setWidgetResizable(True)
            content_SPLIT = QWidget()
            tab_SPLIT.setWidget(content_SPLIT)
            SplitLay = QVBoxLayout(content_SPLIT)
            tab_SPLIT.setWidgetResizable(True)

            content_SEG = QWidget()
            tab_SEG.setWidget(content_SEG)
            SegLay = QVBoxLayout(content_SEG)
            tab_SEG.setWidgetResizable(True)

            tab_HIST.layout = QVBoxLayout()
            HIST_btn_lay = QHBoxLayout()
            self.hist = HistogramPlot()
            tab_HIST.layout.addWidget(self.hist)
            HIST_btn_lay.addWidget(self.UI.PushBtnText("Equalize", lambda: self.HistEqualize(1)))
            HIST_btn_lay.addWidget(self.UI.PushBtnText("CLAHE", lambda: self.HistEqualize(2)))
            tab_HIST.layout.addLayout(HIST_btn_lay)
            tab_HIST.setLayout(tab_HIST.layout)
            FilterLay.addLayout(self.FilterLayout())
            EdgeLay.addLayout(self.EdgeLayout())
            MergeLay.addLayout(self.MergeLayout())
            SplitLay.addLayout(self.SplitLayout())
            SegLay.addLayout(self.SegmentLayout())
            dock_container_layout.addWidget(self.taby)
            dock_container.setLayout(dock_container_layout)
            dock = QDockWidget("Properties", self)
        else:
            dock_container_layout.addWidget(self.UI.prevImg)
            dock_Bottom = QHBoxLayout()
            dock_Bottom.addWidget(self.UI.PushBtnText("APPLY", lambda: self.ApplyRestore(1)))
            dock_Bottom.addWidget(self.UI.PushBtnIcon('TP_assets/love.png', lambda: self.collectionDialog(2), None, (25, 25)))
            dock_Bottom.addWidget(self.UI.PushBtnText("RESTORE", lambda: self.ApplyRestore(3)))
            dock_container_layout.addLayout(dock_Bottom)
            dock_container.setLayout(dock_container_layout)
            dock = QDockWidget("Preview", self)
        dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        dock.setWidget(dock_container)
        dock.setEnabled(False)
        return dock

    def SegmentLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("BACKDROP", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        self.backdrop_image_2 = self.UI.PushBtnIcon("TP_assets/color.png", lambda : self.colorDialog(4), None, size=(150, 150))
        self.spinG_Filter = self.UI.SpinBox(True, 1, 99, 5, 40, True)
        self.spinKMCluster = self.UI.SpinBox(True, 1, 100, 3, 40, ODD=False, action=lambda : self.ThresAdjust(5))
        self.spinSLIC_Seg = self.UI.SpinBox(True, 1, 1000, 30, 50, ODD=False, action=lambda: self.ThresAdjust(6))
        self.spinSLIC_Sigma = self.UI.SpinBox(True, 1, 99, 5, 40, True)
        image_lay = QHBoxLayout()
        image_lay.addWidget(self.backdrop_image_2)
        layout.addLayout(image_lay)
        layout.addWidget(self.UI.Label_TextOnly("THRESHOLD", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        GFilter_lay = QHBoxLayout()
        GFilter_lay.addStretch(2)
        GFilter_lay.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        GFilter_lay.addStretch(1)
        GFilter_lay.addWidget(self.spinG_Filter)
        GFilter_lay.addStretch(2)
        layout.addWidget(self.UI.Label_TextOnly("Gaussian Filter", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(GFilter_lay)
        color_lay = QHBoxLayout()
        color_lay.addWidget(self.UI.PushBtnText("ORI", lambda: self.ThresAdjust(2), ('Calibri', 12), width=91))
        color_lay.addWidget(self.UI.PushBtnText("COL", lambda: self.ThresAdjust(3), ('Calibri', 12), width=91))
        color_lay.addWidget(self.UI.PushBtnText("INV", lambda: self.ThresAdjust(4), ('Calibri', 12), width=91))
        layout.addWidget(self.UI.Label_TextOnly("Masking", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(color_lay)
        layout.addWidget(self.UI.Label_TextOnly("Colour - Thres", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        opt_lay = QHBoxLayout()
        opt_lay.addWidget(self.UI.PushBtnText("ADD", lambda : self.ThresAdjust(1), ('Calibri', 12)))
        opt_lay.addWidget(self.UI.PushBtnText("REMOVE", lambda : self.ThresAdjust(-1), ('Calibri', 12)))
        layout.addLayout(opt_lay)
        self.ColorSeg_spin = []
        self.ColorSeg_label = []
        self.Seg_color = 0
        self.ColorSeg_count = 1
        self.currentSegRC = [0, 2]
        self.segCOLTABLE = self.UI.TableWIDGET(0, 2, (285, 285))
        self.segCOLTABLE.setHorizontalHeaderLabels(['LOW_Thres (HSV)', 'HIGH_Thres (HSV)'])
        self.segCOLTABLE.horizontalHeader().show()
        self.ROWCOL_update(4)
        layout.addWidget(self.segCOLTABLE)
        layout.addWidget(self.UI.PushBtnText("REFRESH", lambda : self.FilterFunc(34), ('Calibri', 12)))
        layout.addWidget(self.UI.Label_TextOnly("Contour - Thres", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinCONT_Thres_low = self.UI.SpinBox(True, 0, 255, 110, 42, action=lambda : self.FilterFunc(35))
        self.spinCONT_Thres_high = self.UI.SpinBox(True, 0, 255, 255, 42, action=lambda : self.FilterFunc(35))
        Bound_check_thres = self.UI.CheckBOX("Mark Boundaries", lambda: self.Seg_OPT(4, Bound_check_thres), True, ('Calibri', 12))
        Mask_check_thres = self.UI.CheckBOX("Mask ALL", lambda: self.Seg_OPT(5, Mask_check_thres), True, ('Calibri', 12))
        opt_Cont = QHBoxLayout()
        opt_Cont.addWidget(self.UI.Label_TextOnly("Thres_LOW", ('Calibri', 11), None, Qt.AlignHCenter, 0))
        opt_Cont.addWidget(self.spinCONT_Thres_low)
        opt_Cont.addWidget(self.UI.Label_TextOnly("Thres_HIGH", ('Calibri', 11), None, Qt.AlignHCenter, 0))
        opt_Cont.addWidget(self.spinCONT_Thres_high)
        layout.addLayout(opt_Cont)
        opt_Cont2 = QHBoxLayout()
        opt_Cont2.addWidget(Bound_check_thres)
        opt_Cont2.addStretch(1)
        opt_Cont2.addWidget(Mask_check_thres)
        layout.addLayout(opt_Cont2)
        self.TH_Bound = True
        self.THCluster_len = 0
        self.THClst_btn = []
        self.THClst_COL = []
        self.TH_mask = []
        self.currentTHClst = [0, 4]
        self.TH_examine = None
        self.TH_clstTABLE = self.UI.TableWIDGET(0, 4, (285, 285))
        self.TH_clstTABLE.setHorizontalHeaderLabels(['Cluster', 'Colour', 'Original', 'Mask'])
        self.TH_clstTABLE.horizontalHeader().show()
        self.TH_clstTABLE.doubleClicked.connect(lambda: self.Seg_OPT(6, None))
        self.ROWCOL_update(7)
        layout.addWidget(self.TH_clstTABLE)
        


        layout.addWidget(self.UI.PushBtnText("REFRESH", lambda: self.FilterFunc(35), ('Calibri', 12)))
        layout.addWidget(self.UI.Label_TextOnly("K-MEANS Clustering", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        opt_KM = QHBoxLayout()
        opt_KM.addStretch(2)
        opt_KM.addWidget(self.UI.Label_TextOnly("CLUSTER", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_KM.addStretch(1)
        opt_KM.addWidget(self.spinKMCluster)
        opt_KM.addStretch(2)
        layout.addLayout(opt_KM)
        self.KMClst_btn = []
        self.KMClst_COL = []
        self.currentKMClst = [0,3]
        self.KM_clstTABLE = self.UI.TableWIDGET(0, 3, (285, 285))
        self.KM_clstTABLE.setHorizontalHeaderLabels(['Cluster', 'Colour', 'Original'])
        self.KM_clstTABLE.horizontalHeader().show()
        self.ROWCOL_update(5)
        layout.addWidget(self.KM_clstTABLE)
        layout.addWidget(self.UI.PushBtnText("REFRESH", lambda: self.FilterFunc(36), ('Calibri', 12)))
        layout.addWidget(self.UI.Label_TextOnly("SLIC Superpixel", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        opt_SLIC = QHBoxLayout()
        opt_SLIC.addWidget(self.UI.Label_TextOnly("Gaussian", ('Calibri', 11), None, Qt.AlignHCenter, 0))
        opt_SLIC.addWidget(self.spinSLIC_Sigma)
        opt_SLIC.addStretch(1)
        opt_SLIC.addWidget(self.UI.Label_TextOnly("n_Segments", ('Calibri', 11), None, Qt.AlignHCenter, 0))
        opt_SLIC.addWidget(self.spinSLIC_Seg)
        layout.addWidget(self.UI.Label_TextOnly("Criteria", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(opt_SLIC)
        opt_SLIC = QHBoxLayout()
        Bound_check = self.UI.CheckBOX("Mark Boundaries", lambda : self.Seg_OPT(1, Bound_check), True, ('Calibri', 12))
        Mask_check = self.UI.CheckBOX("Mask ALL", lambda : self.Seg_OPT(2, Mask_check), True, ('Calibri', 12))
        self.SLIC_Bound = True
        opt_SLIC.addWidget(Bound_check)
        opt_SLIC.addWidget(Mask_check)
        layout.addLayout(opt_SLIC)
        self.SLIC_btn = []
        self.SLIC_COL = []
        self.SLIC_mask = []
        self.currentSLIC = [0, 4]
        self.SLIC_examine = None
        self.reduceSeg = 30
        self.SLIC_TABLE = self.UI.TableWIDGET(0, 4, (285, 285))
        self.SLIC_TABLE.setHorizontalHeaderLabels(['SuperPX', 'Colour', 'Original','Mask'])
        self.SLIC_TABLE.horizontalHeader().show()
        self.SLIC_TABLE.doubleClicked.connect(lambda : self.Seg_OPT(3,None))
        self.ROWCOL_update(6)
        layout.addWidget(self.SLIC_TABLE)
        layout.addWidget(self.UI.PushBtnText("REFRESH", lambda: self.ThresAdjust(6), ('Calibri', 12)))
        return layout

    def Seg_OPT(self, flag, item):
        if flag==1:
            if item.isChecked():
                self.SLIC_Bound = True
            else:
                self.SLIC_Bound = False
        elif flag==4:
            if item.isChecked():
                self.TH_Bound = True
            else:
                self.TH_Bound = False
        elif flag==2:
            if item.isChecked():
                self.SLIC_mask = [True for elem in self.SLIC_mask]
                for row in range(self.reduceSeg):
                    self.SLIC_btn[row][2].setChecked(True)
            else:
                self.SLIC_mask = [False for elem in self.SLIC_mask]
                for row in range(self.reduceSeg):
                    self.SLIC_btn[row][2].setChecked(False)
        elif flag==5:
            if item.isChecked():
                self.TH_mask = [True for elem in self.TH_mask]
                for row in range(self.TH_clstTABLE.rowCount()):
                    self.THClst_btn[row][2].setChecked(True)
            else:
                self.TH_mask = [False for elem in self.TH_mask]
                for row in range(self.TH_clstTABLE.rowCount()):
                    self.THClst_btn[row][2].setChecked(False)
        elif flag==3:
            for currentQTableWidgetItem in self.SLIC_TABLE.selectedItems():
                self.SLIC_examine = currentQTableWidgetItem.row()
        elif flag==6:
            for currentQTableWidgetItem in self.TH_clstTABLE.selectedItems():
                self.TH_examine = currentQTableWidgetItem.row()
        if 1<=flag<=3:
            self.FilterFunc(37)
        else:
            self.FilterFunc(35)

    def ThresAdjust(self, flag):
        if flag==1:
            if self.ColorSeg_count<4:
                self.ColorSeg_count += 1
            self.ROWCOL_update(4)
        elif flag==-1:
            if self.ColorSeg_count>1:
                self.ColorSeg_count -= 1
            self.ROWCOL_update(4)
        elif flag==2:
            self.Seg_color = 0
        elif flag==3:
            self.Seg_color = 1
        elif flag==4:
            self.Seg_color = -1
        elif flag==5:
            self.ROWCOL_update(5)
            self.filterINDEX = 36
        elif flag==6:
            self.reduceSeg = self.spinSLIC_Seg.value()
            self.ROWCOL_update(6)
            self.filterINDEX = 37
        if flag>1:
            self.FilterFunc(self.filterINDEX)

    def Seg_COL_ORI(self, flag, shape):
        if flag==1:
            if 0<=shape[1]<=2:
                color = self.ColorSeg_spin[shape[0]][0].value(), self.ColorSeg_spin[shape[0]][1].value(), self.ColorSeg_spin[shape[0]][2].value()
                col = 0
            else:
                color = self.ColorSeg_spin[shape[0]][3].value(), self.ColorSeg_spin[shape[0]][4].value(), self.ColorSeg_spin[shape[0]][5].value()
                col = 1
            lbl = self.ColorSeg_label[shape[0]][col]
            lbl.setPixmap(self.setPixmap_QtImg(CV.Color_picker(color, (0, 0), hsv=True), 142, 15, False))
            self.FilterFunc(34)
        elif 2<=flag<=4:
            if shape[1]==0:
                col = self.colorDialog(5)
                if col:
                    if flag==2:
                        self.KMClst_COL[shape[0]] = col
                        btn = self.KMClst_btn[shape[0]][shape[1]]
                        self.KMClst_btn[shape[0]][1].setChecked(False)
                    elif flag == 3:
                        self.SLIC_COL[shape[0]] = col
                        btn = self.SLIC_btn[shape[0]][shape[1]]
                        self.SLIC_btn[shape[0]][1].setChecked(False)
                    elif flag==4:
                        self.THClst_COL[shape[0]] = col
                        btn = self.THClst_btn[shape[0]][shape[1]]
                        self.THClst_btn[shape[0]][1].setChecked(False)
                    btn.setIcon(QIcon(self.setPixmap_QtImg(CV.Color_picker(col, (0,0)), btn.width(), btn.height(), False)))
                    btn.setIconSize(QSize(btn.size()))
            elif shape[1]==1:
                if flag==2:
                    check = self.KMClst_btn[shape[0]][shape[1]]
                    btn = self.KMClst_btn[shape[0]][0]
                elif flag==3:
                    check = self.SLIC_btn[shape[0]][shape[1]]
                    btn = self.SLIC_btn[shape[0]][0]
                elif flag==4:
                    check = self.THClst_btn[shape[0]][shape[1]]
                    btn = self.THClst_btn[shape[0]][0]
                if check.isChecked():
                    if flag==2:
                        self.KMClst_COL[shape[0]] = None
                    elif flag==3:
                        self.SLIC_COL[shape[0]] = None
                    elif flag == 4:
                        self.THClst_COL[shape[0]] = None
                    btn.setIcon(QIcon("TP_assets/dropper.png"))
                    btn.setIconSize(QSize(25,25))
                else:
                    if flag==2:
                        self.KMClst_COL[shape[0]] = [0,0,0]
                    elif flag==3:
                        self.SLIC_COL[shape[0]] = [0, 0, 0]
                    elif flag == 4:
                        self.THClst_COL[shape[0]] = [0, 0, 0]
                    btn.setIcon(QIcon(self.setPixmap_QtImg(CV.Color_picker((0,0,0), (0, 0)), btn.width(), btn.height(), False)))
                    btn.setIconSize(QSize(btn.size()))
            elif shape[1]==2:
                if flag==3:
                    check = self.SLIC_btn[shape[0]][shape[1]]
                    if check.isChecked():
                        self.SLIC_mask[shape[0]] = True
                    else:
                        self.SLIC_mask[shape[0]] = False
                elif flag==4:
                    check = self.THClst_btn[shape[0]][shape[1]]
                    if check.isChecked():
                        self.TH_mask[shape[0]] = True
                    else:
                        self.TH_mask[shape[0]] = False
            if flag==2:
                self.FilterFunc(36)
            elif flag==3:
                self.FilterFunc(37)
            elif flag==4:
                self.FilterFunc(35)

    def SplitLayout(self):
        layout = QVBoxLayout()
        SPLIT_RC_lay = QHBoxLayout()
        split_lay = QHBoxLayout()
        self.currentSRC = [2, 2]
        self.spinSplitROW = self.UI.SpinBox(True, 1, 100, 2, 40, action=lambda: self.ROWCOL_update(3))
        self.spinSplitCOL = self.UI.SpinBox(True, 1, 100, 2, 40, action=lambda: self.ROWCOL_update(3))
        self.splitTABLE = self.UI.TableWIDGET(2, 2, (285, 285))
        self.ROWCOL_update(3)
        self.split_image = self.UI.PushBtnIcon("TP_assets/image.png", self.viewAvailableImage, None, size=(150, 150))
        SPLIT_RC_lay.addStretch(1)
        SPLIT_RC_lay.addWidget(self.UI.Label_TextOnly("ROW", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        SPLIT_RC_lay.addWidget(self.spinSplitROW)
        SPLIT_RC_lay.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        SPLIT_RC_lay.addWidget(self.UI.Label_TextOnly("COL", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        SPLIT_RC_lay.addWidget(self.spinSplitCOL)
        SPLIT_RC_lay.addStretch(1)
        layout.addWidget(self.UI.Label_TextOnly("IMAGE", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        split_lay.addWidget(self.split_image)
        layout.addLayout(split_lay)
        layout.addWidget(self.UI.Label_TextOnly("GRID", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(SPLIT_RC_lay)
        layout.addWidget(self.splitTABLE)
        layout.addWidget(self.UI.PushBtnText("REFRESH", self.SplitFunc, ('Calibri', 12)))
        return layout

    def viewAvailableImage(self, shape=None):
        self.imageList_dlg = QDialog(self)
        self.imageList_dlg.setWindowTitle("Image Source")
        dlg_lay = QHBoxLayout()
        list_lay = QVBoxLayout()
        button_lay2 = QVBoxLayout()
        button_lay1 = QHBoxLayout()
        self.ImageSource = QListWidget(self)
        self.ImageSource.setViewMode(QListView.IconMode)
        self.ImageSource.setIconSize(QSize(157, 157))
        self.ImageSource.setFixedSize(190, 250)
        self.ImageSource.itemClicked.connect(lambda: self.ACTIONImageFROMlist(1))
        self.ImageSource_selected = QLabel()
        self.ImageSource_selected.setPixmap(QPixmap.scaled(QPixmap("TP_assets/image.png"), 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
        for img in self.collection:
            self.AddImageTOlist(img)
        button_lay1.addWidget(self.UI.PushBtnText("INSERT", lambda: self.fileDialog(3)))
        color_btn = self.UI.PushBtnText("COLOR", lambda: self.colorDialog(3))
        if self.taby.currentIndex()==4:
            color_btn.setEnabled(False)
        else:
            color_btn.setEnabled(True)
        button_lay1.addWidget(color_btn)
        list_lay.addWidget(self.ImageSource)
        list_lay.addLayout(button_lay1)
        button_lay2.addStretch(2)
        button_lay2.addWidget(self.UI.PushBtnText("APPLY", lambda: self.ACTIONImageFROMlist(5, shape)))
        button_lay2.addStretch(1)
        button_lay2.addWidget(self.UI.PushBtnText("REMOVE", lambda: self.ACTIONImageFROMlist(2)))
        button_lay2.addStretch(1)
        button_lay2.addWidget(self.UI.PushBtnText("CLEAR", lambda: self.ACTIONImageFROMlist(3)))
        button_lay2.addStretch(1)
        button_lay2.addWidget(self.ImageSource_selected)
        dlg_lay.addLayout(list_lay)
        dlg_lay.addLayout(button_lay2)
        self.imageList_dlg.setLayout(dlg_lay)
        self.imageList_dlg.exec_()

    def AddImageTOlist(self, img):
        item = QListWidgetItem(img[1])
        item.setIcon(QIcon(self.setPixmap_QtImg(img[0], 157,157)))
        self.ImageSource.addItem(item)

    def ACTIONImageFROMlist(self, flag, shape=None):
        if flag == 1:  # insert
            collection = self.collection[self.ImageSource.currentRow()]
            self.ImageSource_selected.setPixmap(self.setPixmap_QtImg(collection[0], 100,100, False))
            self.color_backdrop = None  # Not choosing color as backdrop
        elif flag == 2:  # remove
            if self.ImageSource.count() == 0:
                return
            self.collection.pop(self.ImageSource.currentRow())
            self.ImageSource.takeItem(self.ImageSource.currentRow())
        elif flag == 3:  # clear
            self.collection.clear()
            self.ImageSource.clear()
        elif flag == 4:  # Color
            image = np.zeros((100, 100, 3), np.uint8)
            image[:] = self.color_backdrop
            self.ImageSource_selected.setPixmap(self.setPixmap_QtImg(image, 100, 100, False))
            self.ImageSource.clearSelection()
        elif flag == 5:  # apply to backdrop
            if self.taby.currentIndex() == 3 and not self.color_backdrop and self.ImageSource.selectedIndexes() == []:
                    return
            elif self.taby.currentIndex() == 4 and self.ImageSource.selectedIndexes() == []:
                    return
            else:
                if self.color_backdrop or self.color_backdrop_2:
                    if self.taby.currentIndex() == 3:
                        image = CV.Color_picker(self.color_backdrop, (5,8))
                    elif self.taby.currentIndex() == 5:
                        image = CV.Color_picker(self.color_backdrop_2, (5,8))
                else:
                    image = self.collection[self.ImageSource.currentRow()][0]
                if not shape:
                    if self.taby.currentIndex() == 3:   #Merge tab
                        self.MergeWIDTH.setText(str(image.shape[1]))
                        self.MergeHEIGHT.setText(str(image.shape[0]))
                        self.backdrop_image.setIcon(QIcon(self.setPixmap_QtImg(image, 150, 150)))
                        self.image_BACKDROP = [image, True]
                    elif self.taby.currentIndex() == 4: #Split tab
                        self.split_image.setIcon(QIcon(self.setPixmap_QtImg(image, 150, 150)))
                        self.image_SPLIT = [image, True]
                        self.SplitFunc()
                    elif self.taby.currentIndex() == 5: #Segment tab
                        self.backdrop_image_2.setIcon(QIcon(self.setPixmap_QtImg(image, 150, 150)))
                        return
                        # self.image_BACKDROP = [image, True]
                else:
                    if type(shape) == tuple:
                        btn = self.mergeINDbtn[shape[0]][shape[1]][0]
                        btn.setIcon(QIcon(self.setPixmap_QtImg(image, btn.width(), btn.height(), False)))
                        btn.setIconSize(QSize(btn.size()))
                        self.mergeINDbtn[shape[0]][shape[1]][1], self.mergeINDbtn[shape[0]][shape[1]][2] = image, True
                    else:
                        self.CleanSelectedRegion()
                        self.image_backup = self.image_CVT_backup = image
                        self.toolSelected = 1
                        self.complete_selection = self.selection = True
                        self.toolCoords = [0, 0, self.image_backup.shape[1], self.image_backup.shape[0]]
                        image = CV.OverlayImage(self.image_backup.copy(), self.image.copy(), self.toolCoords)
                        CV.drawPrimitive(image, self.toolCoords, 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp
                        self.Render(image)
                self.imageList_dlg.close()
        if 2 <= flag <= 3:
            if self.collection:
                self.ACTIONImageFROMlist(1)
            else:
                self.ImageSource_selected.setPixmap(QPixmap.scaled(QPixmap("TP_assets/image.png"), 100, 100, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

    def SplitFunc(self):
        if not self.image_SPLIT[1]:
            return
        self.sliced_image = []
        h, w, _ = self.image_SPLIT[0].shape
        gapW, gapH = int(w / self.spinSplitCOL.value()), int(h / self.spinSplitROW.value())
        for row in range(self.spinSplitROW.value()):
            sliced_img = []
            for col in range(self.spinSplitCOL.value()):
                image = self.image_SPLIT[0].copy()
                image = CV.CropImage(image, (col * gapW, row * gapH, col * gapW + gapW, row * gapH + gapH))
                sliced_img.append(image)
                btn = self.splitINDbtn[row][col]
                btn.setIcon(QIcon(self.setPixmap_QtImg(image, btn.width(), btn.height(), False)))
                btn.setIconSize(QSize(btn.size()))
                btn.setEnabled(True)
            self.sliced_image.append(sliced_img)

    def MergeFunc(self):
        self.filterINDEX = 15
        w, h = int(self.MergeWIDTH.text()), int(self.MergeHEIGHT.text())
        if not self.image_BACKDROP[1]:
            background = np.zeros((h, w, 3), np.uint8)
            background[:] = (255, 255, 255)
        else:
            background = self.image_BACKDROP[0]
            background = CV.ResizeImage(background, (w, h))
        gapW, gapH = int(w / self.spinMergeCOL.value()), int(h / self.spinMergeROW.value())
        for row in range(self.spinMergeROW.value()):
            for col in range(self.spinMergeCOL.value()):
                if self.mergeINDbtn[row][col][2]:
                    coord = col * gapW, row * gapH
                    image = self.mergeINDbtn[row][col][1]
                    image = CV.ResizeImage(image, (gapW, gapH))
                    background = CV.OverlayImage(image, background, coord)
        self.RenderPreviewIMG(background)
        return background

    def MergeLayout(self):
        layout = QVBoxLayout()
        MERGE_RC_lay = QHBoxLayout()
        MERGE_DIM_lay = QHBoxLayout()
        self.currentMRC = [1, 1]
        self.spinMergeROW = self.UI.SpinBox(True, 1, 100, 1, 40, action=lambda: self.ROWCOL_update(2))
        self.spinMergeCOL = self.UI.SpinBox(True, 1, 100, 1, 40, action=lambda: self.ROWCOL_update(2))
        self.MergeWIDTH = self.UI.LineEdit("1280", size=(55, 25), valid=QIntValidator())
        self.MergeHEIGHT = self.UI.LineEdit("720", size=(55, 25), valid=QIntValidator())
        MERGE_RC_lay.addStretch(1)
        MERGE_RC_lay.addWidget(self.UI.Label_TextOnly("ROW", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_RC_lay.addWidget(self.spinMergeROW)
        MERGE_RC_lay.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        MERGE_RC_lay.addWidget(self.UI.Label_TextOnly("COL", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_RC_lay.addWidget(self.spinMergeCOL)
        MERGE_RC_lay.addStretch(1)
        MERGE_DIM_lay.addWidget(self.UI.Label_TextOnly("WIDTH", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_DIM_lay.addWidget(self.MergeWIDTH)
        MERGE_DIM_lay.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        MERGE_DIM_lay.addWidget(self.UI.Label_TextOnly("HEIGHT", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        MERGE_DIM_lay.addWidget(self.MergeHEIGHT)
        layout.addWidget(self.UI.Label_TextOnly("BACKDROP", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        backdrop_lay = QHBoxLayout()
        self.backdrop_image = self.UI.PushBtnIcon("TP_assets/image.png", self.viewAvailableImage, None, size=(150, 150))
        backdrop_lay.addWidget(self.backdrop_image)
        layout.addLayout(backdrop_lay)
        layout.addWidget(self.UI.Label_TextOnly("DIMENSION", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(MERGE_DIM_lay)
        layout.addWidget(self.UI.Label_TextOnly("GRID", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        layout.addLayout(MERGE_RC_lay)
        self.mergeTABLE = self.UI.TableWIDGET(1, 1, (285, 285))
        self.ROWCOL_update(2)
        layout.addWidget(self.mergeTABLE)
        layout.addWidget(self.UI.PushBtnText("MERGE", self.MergeFunc, ('Calibri', 12)))
        return layout

    def EdgeLayout(self):
        self.spinG_Ksize = self.UI.SpinBox(True, 1, 99, 3, 40, True)
        self.spinThres_low = self.UI.SpinBox(True, 0, 255, 0, 42)
        self.spinThres_high = self.UI.SpinBox(True, 0, 255, 255, 42)
        self.spinS_Ksize = self.UI.SpinBox(True, 1, 9, 3, 40, True)
        self.spinSobel_Ksize = self.UI.SpinBox(True, 1, 9, 3, 40, True)
        layout = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Canny", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        layout.addWidget(self.UI.Label_TextOnly("Gaussian Filter", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_GB = QHBoxLayout()
        opt_GB.addStretch(2)
        opt_GB.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_GB.addStretch(1)
        opt_GB.addWidget(self.spinG_Ksize)
        opt_GB.addStretch(2)
        layout.addLayout(opt_GB)
        layout.addLayout(self.FilterLIST(10))
        layout.addWidget(self.UI.Label_TextOnly("Customization", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_CannyCust = QHBoxLayout()
        opt_CannyCust.addWidget(self.UI.Label_TextOnly("Thres_LOW", ('Calibri', 11), None, Qt.AlignHCenter, 0))
        opt_CannyCust.addWidget(self.spinThres_low)
        opt_CannyCust.addWidget(self.UI.Label_TextOnly("Thres_HIGH", ('Calibri', 11), None, Qt.AlignHCenter, 0))
        opt_CannyCust.addWidget(self.spinThres_high)
        layout.addLayout(opt_CannyCust)
        layout.addLayout(self.FilterLIST(11))
        layout.addWidget(self.UI.Label_TextOnly("Laplacian", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        opt_L = QHBoxLayout()
        opt_L.addStretch(2)
        opt_L.addWidget(self.UI.Label_TextOnly("Sobel KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_L.addStretch(1)
        opt_L.addWidget(self.spinS_Ksize)
        opt_L.addStretch(2)
        layout.addLayout(opt_L)
        layout.addLayout(self.FilterLIST(12))
        layout.addWidget(self.UI.Label_TextOnly("Sobel", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        opt_Sbl = QHBoxLayout()
        opt_Sbl.addStretch(2)
        opt_Sbl.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_Sbl.addStretch(1)
        opt_Sbl.addWidget(self.spinSobel_Ksize)
        opt_Sbl.addStretch(2)
        layout.addLayout(opt_Sbl)
        layout.addLayout(self.FilterLIST(13))
        layout.addWidget(self.UI.Label_TextOnly("Prewitt", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        layout.addLayout(self.FilterLIST(14))
        return layout

    def FilterLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Smoothing", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinKERNEL = self.UI.SpinBox(True, 3, 1000, 3, 40, True)  # restrict even number
        self.spinDEPTH = self.UI.SpinBox(True, 1, 1000, 1, 40)
        self.spinCOLSPACE = self.UI.SpinBox(True, 1, 1000, 1, 40)
        opt_overall = QVBoxLayout()  # add 4 row together
        opt_kernel = QHBoxLayout()
        opt_kernel.addStretch(1)
        opt_kernel.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_kernel.addWidget(self.spinKERNEL)
        opt_kernel.addStretch(1)
        opt_overall.addWidget(self.UI.Label_TextOnly("ALL", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_kernel)
        opt_overall.addLayout(self.FilterLIST(1))
        opt_other = QHBoxLayout()
        opt_other.addWidget(self.UI.Label_TextOnly("Depth", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinDEPTH)
        opt_other.addStretch(1)
        opt_other.addWidget(self.UI.Label_TextOnly("Color|Space", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinCOLSPACE)
        opt_overall.addWidget(self.UI.Label_TextOnly("Bilateral Filter", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_other)
        opt_overall.addLayout(self.FilterLIST(2))
        layout.addLayout(opt_overall)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Sharpening", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinContrast = self.UI.SpinBox(False, 0, 100, 0, 55)
        self.spinSharpenKernel = self.UI.SpinBox(True, 3, 100, 3, 40, True, self.sharpenKernelUPDATE)  # restrict even number
        self.spinSharpenLevel = self.UI.SpinBox(True, 9, 100, 9, 40)  # Limit lower bound
        opt_kernel = QHBoxLayout()
        opt_kernel.addStretch(1)
        opt_kernel.addWidget(self.UI.Label_TextOnly("Contrast LEVEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_kernel.addWidget(self.spinContrast)
        opt_kernel.addStretch(1)
        opt_overall.addWidget(self.UI.Label_TextOnly("Contrasting", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_kernel)
        opt_overall.addLayout(self.FilterLIST(3))
        opt_other = QHBoxLayout()
        opt_other.addWidget(self.UI.Label_TextOnly("KERNEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinSharpenKernel)
        opt_other.addStretch(1)
        opt_other.addWidget(self.UI.Label_TextOnly("LEVEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinSharpenLevel)
        opt_overall.addWidget(self.UI.Label_TextOnly("Sharpening", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_other)
        opt_overall.addLayout(self.FilterLIST(4))
        layout.addLayout(opt_overall)
        self.spinThres = self.UI.SpinBox(True, 0, 255, 127, 42)
        self.spinThresMax = self.UI.SpinBox(True, 0, 255, 255, 42)
        self.spinBlockSize = self.UI.SpinBox(True, 0, 255, 199, 42)
        self.spinConstant = self.UI.SpinBox(True, 0, 255, 5, 42)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Thresholding", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        opt_global = QHBoxLayout()
        opt_global.addWidget(self.UI.Label_TextOnly("Threshold", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_global.addWidget(self.spinThres)
        opt_global.addWidget(self.UI.Label_TextOnly("MaxValue", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_global.addWidget(self.spinThresMax)
        opt_overall.addWidget(self.UI.Label_TextOnly("Global", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_global)
        opt_overall.addLayout(self.FilterLIST(8))
        opt_adapt = QHBoxLayout()
        opt_adapt.addWidget(self.UI.Label_TextOnly("BlockSize", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_adapt.addWidget(self.spinBlockSize)
        opt_adapt.addStretch(1)
        opt_adapt.addWidget(self.UI.Label_TextOnly("Constant", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_adapt.addWidget(self.spinConstant)
        opt_overall.addWidget(self.UI.Label_TextOnly("Adaptive", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_adapt)
        opt_overall.addLayout(self.FilterLIST(9))
        layout.addLayout(opt_overall)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Effects", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.spinBitLevel = self.UI.SpinBox(True, 0, 7, 0, 30)  # 0-7
        opt_overall.addLayout(self.FilterLIST(5))
        opt_other = QHBoxLayout()
        opt_other.addStretch(1)
        opt_other.addWidget(self.UI.Label_TextOnly("Bit LEVEL", ('Calibri', 13), None, Qt.AlignHCenter, 0))
        opt_other.addWidget(self.spinBitLevel)
        opt_other.addStretch(1)
        opt_overall.addWidget(self.UI.Label_TextOnly("Bit Plane Slicing", ('Calibri', 15), '#04c4e0', Qt.AlignHCenter, 0, 30))
        opt_overall.addLayout(opt_other)
        opt_overall.addLayout(self.FilterLIST(6))
        layout.addLayout(opt_overall)
        layout.addLayout(opt_overall)
        opt_overall = QVBoxLayout()
        layout.addWidget(self.UI.Label_TextOnly("Customization", ('Times New Roman', 16), '#00a4bc', Qt.AlignHCenter, 2, 38))
        self.currentROWCOL = [3, 3]
        self.spinROW = self.UI.SpinBox(True, 1, 100, 3, 40, action=lambda: self.ROWCOL_update(1))
        self.spinCOL = self.UI.SpinBox(True, 1, 100, 3, 40, action=lambda: self.ROWCOL_update(1))
        self.customTable = self.UI.TableWIDGET(3, 3, (285, 285))
        delegate = DelegateTable_SpinBox()
        self.customTable.setItemDelegate(delegate)
        customfilterLIST = [("3", "-2", "-3"), ("-4", "8", "-6"), ("5", "-1", "0")]
        for row in range(3):
            for col in range(3):
                item = QTableWidgetItem(customfilterLIST[row][col])
                item.setTextAlignment(Qt.AlignCenter)
                self.customTable.setItem(row, col, item)
        opt_RowCol = QHBoxLayout()
        opt_RowCol.addStretch(1)
        opt_RowCol.addWidget(self.UI.Label_TextOnly("ROW", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        opt_RowCol.addWidget(self.spinROW)
        opt_RowCol.addWidget(self.UI.Label_TextOnly("X", ('Arial', 13), None, Qt.AlignVCenter, 0))
        opt_RowCol.addWidget(self.UI.Label_TextOnly("COL", ('Calibri', 13), None, Qt.AlignVCenter, 0))
        opt_RowCol.addWidget(self.spinCOL)
        opt_RowCol.addStretch(1)
        opt_overall.addLayout(opt_RowCol)
        opt_overall.addWidget(self.customTable)
        opt_overall.addLayout(self.FilterLIST(7))
        layout.addLayout(opt_overall)
        return layout

    def FilterLIST(self, flag):
        layout = QVBoxLayout()
        if flag == 1:
            layout.addWidget(self.UI.PushBtnText("Gaussian-Blur", lambda: self.FilterFunc(3), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Median-Blur", lambda: self.FilterFunc(4), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Average-Blur", lambda: self.FilterFunc(5), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Box-Filter", lambda: self.FilterFunc(6), ('Calibri', 12)))
        elif flag == 2:
            layout.addWidget(self.UI.PushBtnText("Bilateral-Filter", lambda: self.FilterFunc(7), ('Calibri', 12)))
        elif flag == 3:
            layout.addWidget(self.UI.PushBtnText("Contrast", lambda: self.FilterFunc(8), ('Calibri', 12)))
        elif flag == 4:
            layout.addWidget(self.UI.PushBtnText("Sharpen", lambda: self.FilterFunc(9), ('Calibri', 12)))
        elif flag == 5:
            layout.addWidget(self.UI.PushBtnText("Emboss", lambda: self.FilterFunc(10), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Sepia", lambda: self.FilterFunc(11), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("MexicanHat", lambda: self.FilterFunc(12), ('Calibri', 12)))
        elif flag == 6:
            layout.addWidget(self.UI.PushBtnText("Bit-Plane Slice", lambda: self.FilterFunc(13), ('Calibri', 12)))
        elif flag == 7:  # Customize
            layout.addWidget(self.UI.PushBtnText(">>> Customize <<<", lambda: self.FilterFunc(14), ('Calibri', 12)))
        elif flag ==8:
            layout.addWidget(self.UI.PushBtnText("Binary", lambda: self.FilterFunc(16), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Binary_INV", lambda: self.FilterFunc(17), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Trunc", lambda: self.FilterFunc(18), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("ToZERO", lambda: self.FilterFunc(19), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("ToZERO_INV", lambda: self.FilterFunc(20), ('Calibri', 12)))
        elif flag ==9:
            layout.addWidget(self.UI.PushBtnText("Mean Thresholding", lambda: self.FilterFunc(21), ('Calibri', 12)))
            layout.addWidget(self.UI.PushBtnText("Gaussian Thresholding", lambda: self.FilterFunc(22), ('Calibri', 12)))
        elif flag ==10:
            layout = QHBoxLayout()
            layout.addWidget(self.UI.PushBtnText("Wide", lambda: self.FilterFunc(23), ('Calibri', 12), width=91))
            layout.addWidget(self.UI.PushBtnText("Tight", lambda: self.FilterFunc(24), ('Calibri', 12), width=91))
            layout.addWidget(self.UI.PushBtnText("Auto", lambda: self.FilterFunc(25), ('Calibri', 12), width=91))
        elif flag ==11:
            layout.addWidget(self.UI.PushBtnText(">>> Customize <<<", lambda: self.FilterFunc(26), ('Calibri', 12)))
        elif flag ==12:
            layout.addWidget(self.UI.PushBtnText("Laplacian", lambda: self.FilterFunc(27), ('Calibri', 12)))
        elif flag ==13:
            layout = QHBoxLayout()
            layout.addWidget(self.UI.PushBtnText("Sobel_X", lambda: self.FilterFunc(28), ('Calibri', 11), width=90))
            layout.addWidget(self.UI.PushBtnText("Sobel_Y", lambda: self.FilterFunc(29), ('Calibri', 11), width=90))
            layout.addWidget(self.UI.PushBtnText("Sobel_X+Y", lambda: self.FilterFunc(30), ('Calibri', 11), width=93))
        elif flag ==14:
            layout = QHBoxLayout()
            layout.addWidget(self.UI.PushBtnText("Prewitt_X", lambda: self.FilterFunc(31), ('Calibri', 11), width=90))
            layout.addWidget(self.UI.PushBtnText("Prewitt_Y", lambda: self.FilterFunc(32), ('Calibri', 11), width=90))
            layout.addWidget(self.UI.PushBtnText("Prewitt_X+Y", lambda: self.FilterFunc(33), ('Calibri', 11), width=93))
        return layout

    def FilterFunc(self, flag):
        self.CleanSelectedRegion()
        if flag==0:
            return
        if not self.filtered:  # create filter backup image
            self.filtered = True
            self.image_FLT = self.image_CVT.copy()
        self.filterINDEX = flag
        if 3 <= flag <= 6:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, Ksize=self.spinKERNEL.value())
        elif flag == 7:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, depth=self.spinDEPTH.value(), colspace=self.spinCOLSPACE.value())
        elif flag == 8:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, contrast=self.spinContrast.value())
        elif flag == 9:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, Ksize=self.spinSharpenKernel.value(), sharpen=self.spinSharpenLevel.value())
        elif 10 <= flag <= 12:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX)
        elif flag == 13:
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, bitLevel=self.spinBitLevel.value())
        elif flag == 14:
            customFilter = []
            for row in range(self.spinROW.value()):
                newrow = []
                for col in range(self.spinCOL.value()):
                    newrow.append(float(self.customTable.item(row, col).text()))
                customFilter.append(newrow)
            image = CV.Filter(self.image_FLT.copy(), self.filterINDEX, customFilter=customFilter)
        elif 16<=flag<=20:
            image_FLT = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_FLT.copy())
            image = CV.Threshold(image_FLT, self.filterINDEX, thres=self.spinThres.value(), maxThres=self.spinThresMax.value())
        elif 21<=flag<=22:
            image = CV.Threshold(self.image_FLT.copy(), self.filterINDEX, BlockSize=self.spinBlockSize.value(), constant=self.spinConstant.value())
        elif 23<=flag<=25 or 31<=flag<=33:
            image = CV.EdgeDetection(self.image_FLT.copy(), self.filterINDEX, self.spinG_Ksize.value())
        elif flag==26:
            image = CV.EdgeDetection(self.image_FLT.copy(), self.filterINDEX, self.spinG_Ksize.value(), Thres_low=self.spinThres_low.value(), Thres_high=self.spinThres_high.value())
        elif flag==27:
            image = CV.EdgeDetection(self.image_FLT.copy(), self.filterINDEX, self.spinG_Ksize.value(), S_Ksize=self.spinS_Ksize.value())
        elif 28<=flag<=30:
            image = CV.EdgeDetection(self.image_FLT.copy(), self.filterINDEX, self.spinG_Ksize.value(), Ksize=self.spinSobel_Ksize.value())
        elif flag==34:
            Thres = []
            for col in self.ColorSeg_spin:
                Thres.append([(col[0].value(), col[1].value(), col[2].value()), (col[3].value(), col[4].value(), col[5].value())])
            image = CV.Segmentation(self.image_FLT.copy(), self.filterINDEX, G_Filter=self.spinG_Filter.value(), bgCOLOR=self.color_backdrop_2, ThresCOL=Thres, MaskCOL=self.Seg_color)
        elif flag==35:
            cont = CV.CONT_check(self.image_FLT.copy(),G_Filter=self.spinG_Filter.value(), lowThres=self.spinCONT_Thres_low.value(), highThres=self.spinCONT_Thres_high.value())
            self.THCluster_len = len(cont)
            self.ROWCOL_update(7)
            image = CV.Segmentation(self.image_FLT.copy(), self.filterINDEX, G_Filter=self.spinG_Filter.value(), bgCOLOR=self.color_backdrop_2, MaskColor=self.THClst_COL, Contours=cont, Cont_wanted=self.TH_mask, bound= self.TH_Bound, Exam=self.TH_examine, MaskCOL=self.Seg_color )
            self.TH_examine = None
        elif flag==36:
            image = CV.Segmentation(self.image_FLT.copy(), self.filterINDEX, G_Filter=self.spinG_Filter.value(), KM_clst=self.spinKMCluster.value(), MaskColor=self.KMClst_COL)
        elif flag==37:
            if self.reduceSeg == self.spinSLIC_Seg.value():
                newROW = CV.SLIC_check(self.image_FLT.copy(), self.spinSLIC_Sigma.value(), self.spinSLIC_Seg.value())
                if newROW:
                    self.reduceSeg = newROW
                    self.ROWCOL_update(6)
            if self.reduceSeg<self.spinSLIC_Seg.value():
                nseg = self.reduceSeg
            else:
                nseg = self.spinSLIC_Seg.value()
            image = CV.Segmentation(self.image_FLT.copy(), self.filterINDEX, G_Filter=self.spinSLIC_Sigma.value(), bgCOLOR=self.color_backdrop_2, SLIC_nseg=nseg, SLIC_mask=self.SLIC_mask, bound=self.SLIC_Bound, MaskColor=self.SLIC_COL, Exam=self.SLIC_examine)
            self.SLIC_examine = None
        self.RenderPreviewIMG(image)
        self.Render(image)
        return image

    def ApplyRestore(self, flag):
        if flag == 1:  # Apply
            if self.filterINDEX == 15:
                self.image = self.MergeFunc()
                self.image_CVT = self.image.copy()
                self.filtered = False
                self.filterINDEX = 0
                self.collection.append((self.image, "Merge image"))
                self.zoomTool(4)
            else:
                if 1 <= self.filterINDEX <= 2:
                    self.image_FLT = self.HistEqualize(self.filterINDEX)
                elif 3 <= self.filterINDEX <= 14 or 16<= self.filterINDEX <= 37:
                    self.image_FLT = self.FilterFunc(self.filterINDEX)
                self.image_FLT = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_FLT.copy())
                self.image = self.image_FLT
            self.hist.Plot(self.image)
            self.Render(self.image)
        elif flag == 2:  # Collection
            if 1 <= self.filterINDEX <= 2:
                image = self.HistEqualize(self.filterINDEX)
            elif 3 <= self.filterINDEX <= 14 or 16<= self.filterINDEX <= 37:
                image = self.FilterFunc(self.filterINDEX)
            elif self.filterINDEX == 15:
                image = self.MergeFunc()
            else:
                image = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_CVT.copy())
            self.collection.append((image, self.collection_name.text()))
        elif flag == 3:  # Restore
            self.image_FLT = self.image_CVT.copy()
            image_filtering = CV.ConvertColor(self.ColCvt_combo.currentIndex(), self.image_CVT.copy())
            self.RenderPreviewIMG(image_filtering)
            self.hist.Plot(image_filtering)
            self.Render(image_filtering)
            self.filterINDEX = 0  ###########
        elif flag == 4:     # collection for image selection
            if self.toolSelected == 1 and self.complete_selection:
                image = self.image_backup.copy()
            else:
                image = self.image.copy()
            self.collection.append((image, self.collection_name.text()))
        elif type(flag) == tuple:       # collection for sliced image
            image = self.sliced_image[flag[0]][flag[1]].copy()
            self.collection.append((image, self.collection_name.text()))

    def HistEqualize(self, flag):
        self.CleanSelectedRegion()
        if not self.filtered:  # create filter backup image
            self.filtered = True
            self.image_FLT = self.image_CVT.copy()
        self.filterINDEX = flag
        image = CV.Histogram(self.image_FLT.copy(), self.ColCvt_combo.currentIndex(), self.filterINDEX)
        self.RenderPreviewIMG(image)
        self.hist.Plot(image)
        self.Render(image)
        return image

    def zoomTool(self, zoom):
        if self.new:
            self.zoom_slider.setValue(100)
            return
        self.scrollArea.setWidgetResizable(False)
        self.CleanSelectedRegion()
        if zoom==1:
            self.zoom[0] = self.zoom_slider.value() / 100
        else:
            if zoom==2:
                if self.zoom[0]<5:
                    self.zoom[0] += 0.01
            elif zoom==3:
                if self.zoom[0]>0.01:
                    self.zoom[0] -= 0.01
            elif zoom==4:   # actual size
                self.zoom[0] = 1
            self.zoom_slider.setValue(int(self.zoom[0] * 100))
        self.zoom_percentage.setText("\t" + str(int(self.zoom[0] * 100)) + "%")
        self.zoom[1] = self.zoom[0]
        if zoom==5: # fitscreen
            self.scrollArea.setWidgetResizable(True)
            img_w, img_h = self.image.shape[1], self.image.shape[0]
            screen_w, screen_h = self.UI.canvas.size().width(), self.UI.canvas.size().height()
            self.zoom[0] = screen_w / img_w
            self.zoom[1] = screen_h / img_h
            self.zoom_slider.setValue(100)
            self.zoom_percentage.setText("\t" + str(100) + "%")
        self.Render(self.image)

    def moveImage(self, mousepos, image):
        new_coord = (mousepos[0]+self.init_coords[0], mousepos[1]+self.init_coords[1])
        self.toolCoords = [new_coord[0], new_coord[1], new_coord[0]+image.shape[1], new_coord[1]+image.shape[0]]
        CV.drawPrimitive(image, (0,0,image.shape[1]-1, image.shape[0]-1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
        if self.manual_selection:
            temp_image = self.image_backup2.copy()
        else:
            temp_image = self.image.copy()
        temp_image = CV.OverlayImage(image, temp_image, self.toolCoords)
        self.Render(temp_image)

    def Menubars(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu('&File')
        viewMenu = menu.addMenu('&View')
        helpMenu = menu.addMenu('&Help')
        self.UI.MenuDetail(fileMenu, '&New', 'New Page', lambda: self.resizeDialog(True), 'Ctrl+N', 'TP_assets/new.jpg')  # New
        self.UI.MenuDetail(fileMenu, '&Open', 'Open New Project', lambda: self.fileDialog(1), 'Ctrl+O', 'TP_assets/open.jpg')  # Open
        self.UI.MenuDetail(fileMenu, '&Save', 'Save Project', lambda: self.fileDialog(2), 'Ctrl+S', 'TP_assets/save.png')  # Save
        self.UI.MenuDetail(fileMenu, '&Exit', 'Quit Application', lambda: self.UI.QuitDialog(sys), 'Shift+Esc', 'TP_assets/exit.png')  # Exit
        screenMenu = viewMenu.addMenu('Screen')
        self.UI.MenuDetail(screenMenu, 'Actual Size', 'Zoom to 100%', lambda: self.zoomTool(4))
        self.UI.MenuDetail(screenMenu, 'Fit Screen', 'Zoom to fit screen', lambda: self.zoomTool(5))
        gridMenu = viewMenu.addMenu('Gridlines')
        self.grid_list = [self.UI.MenuDetail(gridMenu, 'None', 'default without gridline', lambda: self.grid_option(0), checked=True),
                          self.UI.MenuDetail(gridMenu, 'Standard', '3x3 grid', lambda: self.grid_option(1)),
                          self.UI.MenuDetail(gridMenu, 'Detailed', '10x10 pixels', lambda: self.grid_option(2))]
        self.filtration_show = self.UI.MenuDetail(viewMenu, 'Properties', 'show / hide Properties panel', lambda : self.ShowHide(3), checked=True)
        self.toolbar_show = self.UI.MenuDetail(viewMenu, 'Toolbar', 'show / hide toolbar', lambda : self.ShowHide(2), checked=True)
        self.status_show = self.UI.MenuDetail(viewMenu, 'Status bar', 'show / hide status bar', lambda : self.ShowHide(1), checked=True)
        self.UI.MenuDetail(helpMenu, 'About v_1', 'About the application', lambda : self.UI.about(1))
        self.UI.MenuDetail(helpMenu, 'About v_2', 'About the application', lambda: self.UI.about(2))
        self.UI.MenuDetail(helpMenu, 'About v_3', 'About the application', lambda: self.UI.about(3))

    def Toolbars(self):
        Rot_combo_str = ["Rotate","Rot_Right90"+u'\N{DEGREE SIGN}', "Rot_Left  90"+u'\N{DEGREE SIGN}', "Rotate 180"+u'\N{DEGREE SIGN}', "Flip Vertical", "Flip Horizontal"]
        Rot_combo_icon = ["TP_assets/rot.png", "TP_assets/rot_right.png", "TP_assets/rot_left.png", "TP_assets/rot_half.png", "TP_assets/flip_v.png", "TP_assets/flip_h.png"]
        font_combo_str = ["HersheyComplex", "Her_Complex(S)", "HersheyDuplex", "HersheyPlain", "HersheyScript(C)", "HersheyScript(S)", "HersheyTriplex", "Italic"]
        size_combo_str = ["1px", "2px", "3px", "4px", "5px", "6px", "7px", "8px", "9px", "10px"]
        size_combo_icon = ["TP_assets/1px.png", "TP_assets/2px.png", "TP_assets/3px.png", "TP_assets/4px.png", "TP_assets/5px.png", "TP_assets/6px.png", "TP_assets/7px.png", "TP_assets/8px.png", "TP_assets/9px.png", "TP_assets/10px.png"]
        ColCvt_combo_str = ["RGB image", "Grayscale image", "HSV image", "Hue channel", "Saturation channel", "Value channel", "HSL image", "Light channel", "CIE_L*A*B image", "LUV image", "YCrCb JPEG", "CIE_XYZ image"]
        ColCvt_combo_icon = ["TP_assets/rgb.png", "TP_assets/gray.png", "TP_assets/hsv.png", "TP_assets/hsv2.png", "TP_assets/hsv2.png", "TP_assets/hsv2.png", "TP_assets/hsv.png", "TP_assets/hsv2.png", "TP_assets/hsv.png", "TP_assets/hsv.png", "TP_assets/hsv.png", "TP_assets/hsv.png"]
        self.fontSize = self.UI.SpinBox(False, 0.1, 100, 1, 55, height=30, action=self.FontStyle_Update)
        self.toolbar = QToolBar("Toolbar")
        self.addToolBar(self.toolbar)
        self.SelectionTool = self.UI.ToolButton(self.toolbar, 'TP_assets/selection.png', 'Selection', lambda :self.ToolSelection(1))    #Selection
        self.UI.ToolDetail(self.toolbar, 'TP_assets/crop.jpg', 'Crop', self.CropTool),  # Crop
        self.UI.ToolDetail(self.toolbar, 'TP_assets/resize.png', 'Resize', self.resizeDialog) # Resize
        comboRot = self.UI.ComboBoxDetail(self.toolbar, True, Rot_combo_str, Rot_combo_icon, "Rotation", (115,30), lambda :self.ComboRotation(comboRot))
        self.toolbar.addSeparator()
        self.UI.ToolButton(self.toolbar, 'TP_assets/draw.png', 'Draw', lambda: self.ToolSelection(2))  # Draw
        self.UI.ToolButton(self.toolbar, 'TP_assets/eraser.png', 'Eraser', lambda: self.ToolSelection(9))  # Eraser
        self.UI.ToolButton(self.toolbar, 'TP_assets/dropper.png', 'Color Picker', lambda: self.ToolSelection(10))  # Dropper
        self.UI.ToolButton(self.toolbar, 'TP_assets/text.png', 'Text', lambda: self.ToolSelection(8))  # Text
        self.fontStyle = self.UI.ComboBoxDetail(self.toolbar, False, font_combo_str, None, "Font Style", (120,30), self.FontStyle_Update)
        self.toolbar.addWidget(self.fontSize)
        self.toolbar.addSeparator()
        self.UI.ToolButton(self.toolbar, 'TP_assets/line.png', 'Line', lambda: self.ToolSelection(3))    # Line
        self.UI.ToolButton(self.toolbar, 'TP_assets/circle.png', 'Circle', lambda: self.ToolSelection(4))  # Circle
        self.UI.ToolButton(self.toolbar, 'TP_assets/rect.png', 'Rectangle', lambda: self.ToolSelection(5))   # Rect
        self.UI.ToolButton(self.toolbar, 'TP_assets/triangle.png', 'Triangle', lambda: self.ToolSelection(6))  # Triangle
        self.UI.ToolButton(self.toolbar, 'TP_assets/diamond.png', 'Diamond', lambda: self.ToolSelection(7))  # Diamond
        self.option_btn = self.UI.ToolButton(self.toolbar, 'TP_assets/outline.png', "Outline", self.Outline_Fill, 1, (80,35))
        self.toolbar.addSeparator()
        self.comboSize = self.UI.ComboBoxDetail(self.toolbar, True, size_combo_str, size_combo_icon, "Thickness", (85,30), lambda :self.Outline_Fill(True), (38,30))
        self.colorBtn = self.UI.ToolButton(self.toolbar, 'TP_assets/color.png', "Edit Color", lambda: self.colorDialog(1), 2)
        self.toolbar.addSeparator()
        self.ColCvt_combo = self.UI.ComboBoxDetail(self.toolbar, True, ColCvt_combo_str, ColCvt_combo_icon, "Color Conversion", (165,30), self.Color_Conversion)
        self.toolbar.addSeparator()
        self.UI.ToolDetail(self.toolbar, 'TP_assets/love.png', 'Save as collection', lambda : self.collectionDialog(4))
        self.UI.ToolDetail(self.toolbar, 'TP_assets/addlove.png', 'Insert from collection', lambda: self.viewAvailableImage(True))
        self.toolbar.setEnabled(False)

    def UpdateText(self):
        image = self.image_backup.copy()
        CV.drawText(image, self.TextEdit.text(), self.init_coords, self.font[0], self.font[1], self.color, self.thickness)
        self.Render(image)

    def FontStyle_Update(self):
        if not self.toolSelected==8:
            return
        self.font[0] = self.fontStyle.currentIndex()
        self.font[1] = self.fontSize.value()
        self.UpdateText()

    def ShowHide(self, flag):
        if flag==1: #status
            if self.status_show.isChecked():
                self.statusBar().show()
            else:
                self.statusBar().hide()
        elif flag==2:   #toolbar
            if self.toolbar_show.isChecked():
                self.toolbar.show()
            else:
                self.toolbar.hide()
        elif flag==3:   #Filtration
            if self.filtration_show.isChecked():
                self.dockProperties.show()
                self.dockPreview.show()
            else:
                self.dockProperties.hide()
                self.dockPreview.hide()

    def ComboRotation(self, comboRot):
        index = comboRot.currentIndex()
        if index == 0 or self.new:
            comboRot.setCurrentIndex(0)
            return
        comboRot.blockSignals(True)
        if self.selection:
            image = self.image_backup.copy()
            if self.manual_selection:
                temp_image = self.image_backup2.copy()
            else:
                temp_image = self.image.copy()
            image2 = self.image_CVT_backup.copy()

            image2, _ = CV.RotateImage(image2, self.toolCoords, index)
            image, self.toolCoords = CV.RotateImage(image, self.toolCoords, index)
            self.image_backup = image.copy()           # renew n save latest image
            self.image_CVT_backup = image2.copy()      # renew n save latest image
            CV.drawPrimitive(image, (0, 0, image.shape[1] - 1, image.shape[0] - 1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
            temp_image = CV.OverlayImage(image, temp_image, self.toolCoords)
        else:
            self.image, self.toolCoords = CV.RotateImage(self.image.copy(), (0,0,self.image.shape[1], self.image.shape[0]), index)
            self.image_CVT, _ = CV.RotateImage(self.image_CVT.copy(), (0,0,self.image_CVT.shape[1], self.image_CVT.shape[0]), index)
            temp_image = self.image
        self.Render(temp_image)
        comboRot.setCurrentIndex(0)
        comboRot.blockSignals(False)

    def ToolSelection(self, slc):
        if self.new:
            return
        self.CleanSelectedRegion()
        self.toolSelected = slc
        if self.toolSelected==2 or self.toolSelected==3 or 8<=self.toolSelected<=10:
            self.Outline_Fill()

    def CleanSelectedRegion(self):
        if self.toolSelected == 1 and self.selection:
            self.selection = self.Move = self.complete_selection = self.manual_selection = False
            self.image = CV.OverlayImage(self.image_backup.copy(), self.image, self.toolCoords)
            image2 = self.image_CVT_backup.copy()
            self.image_CVT = CV.OverlayImage(image2, self.image_CVT, self.toolCoords)

    def Color_Conversion(self):
        if self.new:
            self.ColCvt_combo.setCurrentIndex(0)
            return
        self.CleanSelectedRegion()
        if self.filtered:
            ori_image = self.image_FLT.copy()
        else:
            ori_image = self.image_CVT.copy()
        self.image = CV.ConvertColor(self.ColCvt_combo.currentIndex(), ori_image)
        self.Render(self.image)
        self.RenderPreviewIMG(self.image)
        self.hist.Plot(self.image)

    def Outline_Fill(self, flag=None):
        if flag:
            self.thickness = self.comboSize.currentIndex()+1
        else:
            if self.thickness!=-1 and 4<=self.toolSelected<=7:
                self.option_btn.setText("Fill")
                self.option_btn.setIcon(QIcon('TP_assets/fill.png'))
                self.thickness = -1
            else:
                self.option_btn.setText("Outline")
                self.option_btn.setIcon(QIcon('TP_assets/outline.png'))
                self.thickness = self.comboSize.currentIndex()+1
        if self.point:
            self.UpdateText()

    def CropTool(self):
        if not self.selection:
            return
        self.selection = self.Move = self.complete_selection = self.manual_selection = False
        self.image = self.image_backup.copy()
        self.Render(self.image)
        self.image_CVT = self.image_CVT_backup.copy()

    def HV_input(self, hv):
        if self.Aspc_ratio:
            if hv=='h':
                self.v_input.setText(self.h_input.text())
            elif hv=='v':
                self.h_input.setText(self.v_input.text())

    def By_resize(self):
        if self.by_2.isChecked():
            self.resize_value[0], self.resize_value[1] = self.h_input.text(), self.v_input.text()
            self.h_input.blockSignals(True)
            self.v_input.blockSignals(True)
            self.h_input.setText(str(self.resize_value[2]))
            self.v_input.setText(str(self.resize_value[3]))
            self.h_input.blockSignals(False)
            self.v_input.blockSignals(False)
        elif self.by_1.isChecked():
            self.resize_value[2], self.resize_value[3] = self.h_input.text(), self.v_input.text()
            self.h_input.blockSignals(True)
            self.v_input.blockSignals(True)
            self.h_input.setText(str(self.resize_value[0]))
            self.v_input.setText(str(self.resize_value[1]))
            self.h_input.blockSignals(False)
            self.v_input.blockSignals(False)

    def AspectRatio(self):
        if self.Aspc_ratio:
            self.Aspc_ratio = False
        else:
            self.Aspc_ratio = True

    def CollectionSave(self, dlg, flag):
        dlg.close()
        self.ApplyRestore(flag)

    def collectionDialog(self, flag):
        dlg = QDialog(self)
        dlg.setFixedSize(300,50)
        dlg.setWindowTitle("Save Collection")
        layout = QHBoxLayout()
        self.collection_name = self.UI.LineEdit("Untitled collection", size=(150,25))
        layout.addWidget(self.UI.Label_TextOnly("Collection", font=('Georgia', 11)))
        layout.addWidget(self.collection_name)
        layout.addWidget(self.UI.PushBtnIcon("TP_assets/save.png", lambda : self.CollectionSave(dlg, flag)))
        dlg.setLayout(layout)
        dlg.exec_()

    def resizeOption(self, dlg, flag=None):
        dlg.close()
        w, h = int(self.h_input.text()), int(self.v_input.text())
        if w==0:
            w = 1
        if h==0:
            h = 1
        if flag:    # new page
            self.image = CV.ResizeImage(self.image, (w, h))
            self.colorDialog(2)
            return
        if self.selection:
            image = self.image_backup.copy()
            image2 = self.image_CVT_backup.copy()
        else:
            image = self.image.copy()
            image2 = self.image_CVT.copy()
        if self.by_1.isChecked():
            w, h = int(w / 100 * image.shape[1]), int(h / 100 * image.shape[0])
            image = CV.ResizeImage(image, (w, h))
            image2 = CV.ResizeImage(image2, (w, h))
        else:
            image = CV.ResizeImage(image, (w, h))
            image2 = CV.ResizeImage(image2, (w, h))
        self.image_backup = image.copy()
        self.image_CVT_backup = image2.copy()
        if not self.selection:
            self.image = image
            self.image_CVT = image2
        else:
            CV.drawPrimitive(image, (0, 0, image.shape[1] - 1, image.shape[0] - 1), 1, None, int(2 / max(self.zoom[0], self.zoom[1])))  # only using backup image to bit since temp   #dash line
            temp_image = self.image_backup2.copy()
            center = self.toolCoords[0]+(self.toolCoords[2]-self.toolCoords[0])//2, self.toolCoords[1]+(self.toolCoords[3]-self.toolCoords[1])//2
            self.toolCoords = [center[0]-w//2, center[1]-h//2, center[0]+w//2, center[1]+h//2]
            image = CV.OverlayImage(image, temp_image, self.toolCoords)
        self.Render(image)
        self.Aspc_ratio = True

    def resizeDialog(self, flag=None):
        if flag:    # New Page
            self.image = np.zeros((500, 500, 3), np.uint8)
        if self.selection:
            image = self.image_backup.copy()
            self.resize_value[2], self.resize_value[3] = image.shape[1], image.shape[0]
        else:
            self.resize_value[2], self.resize_value[3] = self.image.shape[1], self.image.shape[0]
        dlg = QDialog(self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.setFixedSize(300,250)
        main_layout = QVBoxLayout()
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        if flag:
            dlg.setWindowTitle("Dimension")
            text1 = self.UI.Label_TextOnly("By pixels:", ('Times New Roman', 12))
            layout1.addWidget(text1)
            text = '500'
        else:
            dlg.setWindowTitle("Resize")
            text1 = self.UI.Label_TextOnly("By: ", ('Times New Roman', 12))
            layout1.addWidget(text1)
            layout1.addStretch(1)
            self.by_1 = QRadioButton(self)
            self.by_1.setText("Percentage")
            self.by_1.setFont(QFont('Times New Roman', 11))
            self.by_1.setChecked(True)
            layout1.addWidget(self.by_1)
            layout1.addStretch(1)
            self.by_2 = QRadioButton(self)
            self.by_2.setText("Pixel    ")
            self.by_2.setFont(QFont('Times New Roman', 11))
            self.by_2.toggled.connect(self.By_resize)
            layout1.addWidget(self.by_2)
            text = '100'
        h_label = QLabel(self)
        h_label.setPixmap(QPixmap("TP_assets/horizontal.png"))
        layout2.addWidget(h_label)
        layout2.addStretch(1)
        h_text = self.UI.Label_TextOnly("Horizontal :", ('Times New Roman', 11))
        layout2.addWidget(h_text)
        layout2.addStretch(1)
        self.h_input = self.UI.LineEdit(text, lambda :self.HV_input('h'), (60, 30), QIntValidator())
        layout2.addWidget(self.h_input)
        v_label = QLabel(self)
        v_label.setPixmap(QPixmap("TP_assets/vertical.png"))
        layout3.addWidget(v_label)
        layout3.addStretch(1)
        v_text = self.UI.Label_TextOnly("Vertical :", ('Times New Roman', 11))
        layout3.addWidget(v_text)
        layout3.addStretch(1)
        self.v_input = self.UI.LineEdit(text, lambda :self.HV_input('v'), (60, 30), QIntValidator())
        layout3.addWidget(self.v_input)
        ratio_check = QCheckBox(self)
        ratio_check.setChecked(True)
        ratio_check.setText("Maintain aspect ratio")
        ratio_check.stateChanged.connect(self.AspectRatio)
        option_btn = self.UI.PushBtnText("APPLY", lambda : self.resizeOption(dlg, flag))
        main_layout.addLayout(layout1)
        main_layout.addStretch(1)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout3)
        main_layout.addStretch(1)
        main_layout.addWidget(ratio_check)
        main_layout.addWidget(option_btn)
        dlg.setLayout(main_layout)
        dlg.exec_()

    def newLAUNCH(self):
        self.selection = self.Move = self.complete_selection = self.manual_selection = False
        self.zoomTool(4)
        self.ColCvt_combo.setCurrentIndex(0)
        self.Render(self.image)
        for atr in self.grid_list:
            atr.setCheckable(True)

    def colorDialog(self, flag):
        dlg = QColorDialog(self)
        dlg.setWindowModality(Qt.ApplicationModal)
        col = QColorDialog.getColor()
        if col.isValid():
            if flag==1:     # edit color
                self.color = tuple(reversed(col.getRgb()[:3]))
                self.colorBtn.setIcon(QIcon(self.setPixmap_QtImg(CV.Color_picker(self.color), 45,45, False)))
                if self.point:
                    self.UpdateText()
            elif flag==2:   # open new page color
                if self.new:
                    self.new = False
                    self.toolbar.setEnabled(True)
                    self.dockPreview.setEnabled(True)
                    self.dockProperties.setEnabled(True)
                self.color_bg = tuple(reversed(col.getRgb()[:3]))
                self.image[:] = self.color_bg
                self.image_CVT = self.image
                self.newLAUNCH()
            elif flag==3:   #Merge de color backdrop
                self.color_backdrop = tuple(reversed(col.getRgb()[:3]))
                self.ACTIONImageFROMlist(4)
            elif flag==4:   #Seg tab de color backdrop
                self.color_backdrop_2 = tuple(reversed(col.getRgb()[:3]))
                self.ACTIONImageFROMlist(5)
            elif flag==5:   #Seg tab de color dropper
                return tuple(reversed(col.getRgb()[:3]))
        else:
            if flag==5:
                return None

    def fileDialog(self, flag):
        filter = "Images (*.png *.jpg *.tif)"
        if flag==1:     #open
            file, _ = QFileDialog.getOpenFileName(self, "File Directory", QDir.currentPath(), filter)
            if file == (""):
                return
            if self.new:
                self.new = False
                self.toolbar.setEnabled(True)
                self.dockPreview.setEnabled(True)
                self.dockProperties.setEnabled(True)
            self.color_bg = (255, 255, 255)
            self.image = CV.LoadImage(file)
            self.image_CVT = CV.LoadImage(file) # creating image backup for Conversion
            self.filtered = False
            self.hist.Plot(self.image)
            self.RenderPreviewIMG(self.image)
            self.collection.append((self.image, os.path.basename(file)))
            self.newLAUNCH()
        elif flag==3:
            file, _ = QFileDialog.getOpenFileName(self, "File Directory", QDir.currentPath(), filter)
            if file == (""):
                return
            self.collection.append((CV.LoadImage(file), os.path.basename(file)))
            self.AddImageTOlist(self.collection[-1])
            self.ImageSource.setCurrentRow(len(self.collection)-1)
            self.ACTIONImageFROMlist(1)
        elif flag==2:   #save
            file, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.currentPath(), "PNG(*.png);;JPEG(*.jpg *.jpeg)")
            if file == ("") or self.new:
                return
            status = CV.SaveImage(file, self.image)
            if status:
                self.UI.InfoDialog(file)

    def grid_option(self, value):
        if self.new:
            return
        for grid in self.grid_list:
            grid.setChecked(False)
        self.grid_list[value].setChecked(True)

        self.grid = value
        self.Render(self.image)

    def Grid(self, image):
        image = image.copy()
        if self.grid == 1:   # 3x3grid
            CV.drawPrimitive(image, (0, image.shape[0] // 3, image.shape[1], image.shape[0] // 3), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (0, image.shape[0] // 3 * 2, image.shape[1], image.shape[0] // 3 * 2), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (image.shape[1]//3, 0, image.shape[1]//3, image.shape[0]), 3, (123, 123, 123), 1)
            CV.drawPrimitive(image, (image.shape[1]//3*2, 0, image.shape[1]//3*2, image.shape[0]), 3, (123, 123, 123), 1)
        elif self.grid == 2: # 10x10px
            for i in range(1, int(image.shape[1]/10)+1):
                CV.drawPrimitive(image, (10*i, 0, 10*i, image.shape[0]), 2, (150, 150, 150), 1)
            for i in range(1, int(image.shape[0]/10)+1):
                CV.drawPrimitive(image, (0, 10*i, image.shape[1], 10*i), 2, (150, 150, 150), 1)
        return image

    def setPixmap_QtImg(self, image, width, height, Keep=True):
        image_RGBA = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        QtImg = QImage(image_RGBA.data, image_RGBA.shape[1], image_RGBA.shape[0], QImage.Format_ARGB32)
        if Keep:
            KAR = Qt.KeepAspectRatio
        else:
            KAR = Qt.IgnoreAspectRatio
        return QPixmap.scaled(QPixmap.fromImage(QtImg), width, height, KAR, Qt.SmoothTransformation)

    def RenderPreviewIMG(self, image):
        self.UI.prevImg.setPixmap(self.setPixmap_QtImg(image, 250,250))

    def Render(self, image):
        image = self.Grid(image)
        self.UI.canvas.setPixmap(self.setPixmap_QtImg(image, int(image.shape[1]*self.zoom[0]), int(image.shape[0]*self.zoom[1])))
        self.UI.canvas.resize(int(image.shape[1]*self.zoom[0]), int(image.shape[0]*self.zoom[1]))
        self.pixel_dim.setText("Dimension : "+str(image.shape[1])+" x "+str(image.shape[0])+'px\t')

def main():
    app = QApplication(sys.argv)
    win = Paint()
    win.show()
    sys.exit(app.exec_())

if __name__=='__main__':
    main()

