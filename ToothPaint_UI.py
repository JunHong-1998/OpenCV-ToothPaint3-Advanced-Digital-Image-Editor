from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import time

class WidgetUI(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.canvas = self.CanvasLabel(True, True, Qt.AlignTop)
        self.prevImg = self.CanvasLabel(False, True, Qt.AlignCenter)

    def CanvasLabel(self, SizeIgnore, Scale, Align):
        canvas = QLabel(self)
        if SizeIgnore:
            canvas.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        canvas.setScaledContents(Scale)
        canvas.setAlignment(Align)
        return canvas

    def TableWIDGET(self, row, col, size, ScrollBar=True):
        Table = QTableWidget(self)
        Table.setRowCount(row)
        Table.setColumnCount(col)
        if size:
            Table.setFixedSize(size[0], size[1])
        Table.horizontalHeader().hide()
        Table.verticalHeader().hide()
        Table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        Table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        if not ScrollBar:
            Table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            Table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return Table

    def CheckBOX(self, name, action, checked, font=None):
        checkbox = QCheckBox(self)
        if name:
            checkbox.setText(name)
        if checked:
            checkbox.setChecked(True)
        if font:
            checkbox.setFont(QFont(font[0], font[1]))
        if action:
            checkbox.clicked.connect(action)
        return checkbox

    def ToolButton(self, toolbar, icon, name, action, flag=None, icon_size=None):
        ToolBtn = QToolButton(self)
        ToolBtn.setIcon(QIcon(icon))
        ToolBtn.setToolTip(name)
        if icon_size:
            ToolBtn.setFixedSize(icon_size[0], icon_size[1])
        if flag==1:
            ToolBtn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            ToolBtn.setText(name)
            toolbar.addWidget(ToolBtn)
            ToolBtn.clicked.connect(action)
            return ToolBtn
        elif flag==2:
            toolbar.addWidget(ToolBtn)
            ToolBtn.clicked.connect(action)
            return ToolBtn
        ToolBtn.setCheckable(True)
        ToolBtn.setAutoExclusive(True)
        toolbar.addWidget(ToolBtn)
        ToolBtn.clicked.connect(action)
        return ToolBtn

    def ToolDetail(self, toolbar, icon, name, action):
        ToolAct = QAction(QIcon(icon), name, self)
        ToolAct.triggered.connect(action)
        toolbar.addAction(ToolAct)

    def ComboBoxDetail(self, Layout, icon, combo_str, combo_icon, name, size, action, icon_size=None, height=None):
        combo = QComboBox(self)
        combo.setToolTip(name)
        if size:
            combo.setFixedSize(size[0], size[1])
        if height:
            combo.setFixedHeight(height)
        if icon:
            for r in range(len(combo_icon)):
                combo.addItem(QIcon(combo_icon[r]), combo_str[r])
                if icon_size:
                    combo.setIconSize(QSize(icon_size[0], icon_size[1]))
        else:
            for f in combo_str:
                combo.addItem(f)
        if action:
            combo.currentIndexChanged.connect(action)
        if Layout:
            Layout.addWidget(combo)
        return combo

    def StatusBAR(self, statusbar, statusLIST):
        statusbar.setStyleSheet('background-color: #e3e3e3;QStatusBar::item {border: none;}')
        for status in statusLIST:
            if not status:
                statusbar.addPermanentWidget(VLine())
            else:
                statusbar.addPermanentWidget(status)

    def SpinBox(self, flag, min, max, value, width=None, ODD=None, action=None, height=None):
        if flag:
            if ODD:
                spin = SpinBox()
                spin.setSingleStep(2)
            else:
                spin = QSpinBox(self)
        else:
            spin = QDoubleSpinBox(self)
            spin.setSingleStep(0.1)
        spin.setMinimum(min)
        if width:
            spin.setFixedWidth(width)
        if max:
            spin.setMaximum(max)
        spin.setValue(value)
        if height:
            spin.setFixedHeight(height)
        if action:
            spin.valueChanged.connect(action)
        return spin

    def LineEdit(self, text, action=None, size=None, valid=None):
        LE = QLineEdit(self)
        LE.setText(text)
        if size:
            LE.setFixedSize(size[0], size[1])
        if valid:
            LE.setValidator(valid)
        if action:
            LE.textChanged.connect(action)
        return LE

    def Label_TextOnly(self, text, font=None, color=None, align=None, border=None, height=None):
        label_Text = QLabel(self)
        label_Text.setText(text)
        if font:
            label_Text.setFont(QFont(font[0], font[1]))
        if height:
            label_Text.setFixedHeight(height)
        if align:
            label_Text.setAlignment(align)
        if color and border:
            label_Text.setStyleSheet("background-color: {}".format(color)+"; border: {}px solid black".format(border))
        elif color:
            label_Text.setStyleSheet("background-color: {}".format(color))
        return label_Text

    def PushBtnText(self, text, action, font=None, width=None):
        btn = QPushButton(self)
        btn.setText(text)
        if font:
            btn.setFont(QFont(font[0], font[1]))
        if width:
            btn.setFixedWidth(width)
        btn.clicked.connect(action)
        return btn

    def PushBtnIcon(self, icon, action, border=None, size=None, iconSize=None, enable=True):
        btn = QPushButton(self)
        btn.setIcon(QIcon(icon))
        if not border:
            btn.setStyleSheet("background-color: transparent")
        if size:
            btn.setIconSize(QSize(size[0], size[1]))
            btn.setFixedSize(size[0], size[1])
        if iconSize:
            btn.setIconSize(QSize(iconSize[0], iconSize[1]))
        if not enable:
            btn.setEnabled(False)
        if action:
            btn.clicked.connect(action)
        return btn

    def MenuDetail(self, menu, name, statusTip, action=None, shortcutKey=None, icon=None, checked = None):
        if icon:
            MenuAct = QAction(QIcon(icon),name,self)
        else:
            MenuAct = QAction(name, self)
        if shortcutKey:
            MenuAct.setShortcut(shortcutKey)
        MenuAct.setStatusTip(statusTip)
        if checked:
            MenuAct.setCheckable(True)
            MenuAct.setChecked(True)
        if action:
            MenuAct.triggered.connect(action)
        menu.addAction(MenuAct)
        return MenuAct

    def InfoDialog(self, filepath):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText("Your Project is compiled and saved successfully")
        msg.setWindowTitle("File Saved")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDetailedText("The filepath is as follow:\n"+filepath)
        msg.exec_()

    def about(self, flag):
        msg = QDialog(self)
        msg.setWindowTitle("ABOUT Tooth Paint")
        about_label = QLabel(self)
        if flag==1:
            image = "TP_assets/about.png"
        elif flag==2:
            image = "TP_assets/about2.png"
        elif flag==3:
            image = "TP_assets/about3.png"
        about_label.setPixmap(QPixmap(image))
        layout = QVBoxLayout(self)
        layout.addWidget(about_label)
        msg.setLayout(layout)
        msg.exec_()

    def QuitDialog(self, sys):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Are you sure to quit application")
        msg.setInformativeText("Reminder: Save your project before quit")
        msg.setWindowTitle("Quit")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        quit = msg.exec_()
        if quit==16384:
            sys.exit()

    def SliderWidget(self, ott, default, min, max, width, action):
        slider = QSlider(self)
        slider.setOrientation(ott)
        slider.setValue(default)
        slider.setMinimum(min)
        slider.setMaximum(max)
        slider.setFixedWidth(width)
        slider.valueChanged.connect(action)
        slider.setStyleSheet("QSlider::groove:horizontal {border: 1px solid #bbb;background: white;height: 10px;border-radius: 4px;}"
                             "QSlider::sub-page:horizontal {background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,stop: 0 #66e, stop: 1 #bbf);background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,stop: 0 #bbf, stop: 1 #55f);border: 1px solid #777;height: 10px;border-radius: 4px;}"
                             "QSlider::add-page:horizontal {background: #fff;border: 1px solid #777;height: 10px;border-radius: 4px;}"
                             "QSlider::handle:horizontal {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #eee, stop:1 #ccc);border: 1px solid #777;width: 13px;margin-top: -2px;margin-bottom: -2px;border-radius: 4px;}"
                             "QSlider::handle:horizontal:hover {background: qlineargradient(x1:0, y1:0, x2:1, y2:1,stop:0 #fff, stop:1 #ddd);border: 1px solid #444;border-radius: 4px;}"
                             "QSlider::sub-page:horizontal:disabled {background: #bbb;border-color: #999;}"
                             "QSlider::add-page:horizontal:disabled {background: #eee;border-color: #999;}"
                             "QSlider::handle:horizontal:disabled {background: #eee;border: 1px solid #aaa;border-radius: 4px;}")
        return slider

    def SplashScreen(self):
        splash = QSplashScreen(QPixmap("TP_assets/splashscreen3.png"), Qt.WindowStaysOnTopHint)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        progress_bar = QProgressBar(splash)
        progress_bar.setStyleSheet("QProgressBar {border: 1px solid black;text-align: top;padding: 2px;border-radius: 7px;"
                                   "background: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #fff,stop: 0.4999 #eee,stop: 0.5 #ddd,stop: 1 #eee );height: 11px}"
                                   "QProgressBar::chunk {background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0,stop: 0 #ea00ff,stop: 1 #68fdff );"
                                   "border-top-left-radius: 7px;border-radius: 7px;border: None;}")
        progress_bar.setFixedWidth(530)
        progress_bar.move(120, 570)

        Loading_text = QLabel(splash)
        Loading_text.setFont(QFont("Calibri", 11))
        Loading_text.setStyleSheet("QLabel { background-color : None; color : #c12cff; }")
        Loading_text.setGeometry(125, 585, 300, 50)
        text = ("Initializing...", "Getting path...", "Measuring memory...", "Scanning for plugs in...", "Initializing panels...", "Loading library...", "Building color conversion tables...", "Reading tools...", "Reading Preferences...", "Getting ready...")
        splash.show()
        for i in range(0, 101):
            if i < 20:
                Loading_text.setText(text[0])
            elif i < 28:
                Loading_text.setText(text[1])
            elif i < 34:
                Loading_text.setText(text[2])
            elif i < 45:
                Loading_text.setText(text[3])
            elif i < 53:
                Loading_text.setText(text[4])
            elif i < 60:
                Loading_text.setText(text[5])
            elif i < 68:
                Loading_text.setText(text[6])
            elif i < 75:
                Loading_text.setText(text[7])
            elif i < 89:
                Loading_text.setText(text[8])
            else:
                Loading_text.setText(text[9])
            progress_bar.setValue(i)
            t = time.time()
            while time.time() < t + 0.035:
                QApplication.processEvents()
        time.sleep(1)
class SpinBox(QSpinBox):
    # Replaces the valueChanged signal
    newValueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(SpinBox, self).__init__(parent=parent)

        self.valueChanged.connect(self.onValueChanged)
        self.before_value = self.value()

    def onValueChanged(self, i):
        if not self.isValid(i):
            self.setValue(self.before_value)
        else:
            self.newValueChanged.emit(i)
            self.before_value = i

    def isValid(self, value):
        if (value % self.singleStep()) == 0:
            return False
        return True

class DelegateTable_SpinBox(QItemDelegate):

    def createEditor(self, parent, option, index):
        spinbox = QDoubleSpinBox(parent)
        spinbox.setMinimum(-1000)
        spinbox.setMaximum(1000)
        return spinbox

class VLine(QFrame):
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

class MouseTracker(QObject):
    positionChanged = pyqtSignal(QPoint)

    def __init__(self, widget):
        super().__init__(widget)
        self._widget = widget
        self.widget.setMouseTracking(True)
        self.widget.installEventFilter(self)

    @property
    def widget(self):
        return self._widget

    def eventFilter(self, o, e):
        if o is self.widget and e.type() == QEvent.MouseMove:
            self.positionChanged.emit(e.pos())
        return super().eventFilter(o, e)

