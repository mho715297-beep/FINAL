import importlib
import core.MayaWidget
importlib.reload(core.MayaWidget)
from core.MayaWidget import MayaWidget  # Calling to the MayaWidget file to get the commands

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QSizePolicy
# Above is the imported Widget information
import maya.cmds as mc

# The Pivot functions within the widget. The major mechanics within the widget for the pivot reset functions
class PivotTool:
    def __init__(self):
        self.storedPivots = {}  # Stores original pivot positions keyed by object name

    def _GetSelectedObjects(self):
        """Return the current selection, or print a warning and return None."""
        selected = mc.ls(sl=True, transforms=True)
        if not selected:
            print("PivotTool: No objects selected.")
            return None
        return selected

    def _SetPivot(self, obj, x, y, z):
        """Move both the rotate and scale pivot of obj to (x, y, z) in world space."""
        mc.xform(obj, worldSpace=True, rotatePivot=[x, y, z])
        mc.xform(obj, worldSpace=True, scalePivot=[x, y, z])

    def StorePivotPositions(self):
        """Store the current pivot positions of all selected objects so they can be restored later."""
        objs = self._GetSelectedObjects()
        if not objs:
            return

        for obj in objs:
            rp = mc.xform(obj, q=True, worldSpace=True, rotatePivot=True)
            self.storedPivots[obj] = rp
            print(f"PivotTool: Stored pivot for '{obj}' at {rp}")

        print(f"PivotTool: {len(objs)} pivot(s) stored.")

    def ResetPivotToWorldOrigin(self):
        """Set the pivot of all selected objects to (0, 0, 0) in world space."""
        objs = self._GetSelectedObjects()
        if not objs:
            return

        for obj in objs:
            self._SetPivot(obj, 0.0, 0.0, 0.0)
            print(f"PivotTool: Pivot reset to world origin for '{obj}'")

    def ResetPivotToOriginalPosition(self):
        """Restore each selected object's pivot to its stored original position."""
        objs = self._GetSelectedObjects()
        if not objs:
            return

        for obj in objs:
            if obj not in self.storedPivots:
                print(f"PivotTool: No stored pivot found for '{obj}'. Click 'Store Pivots' first.")
                continue

            rp = self.storedPivots[obj]
            self._SetPivot(obj, rp[0], rp[1], rp[2])
            print(f"PivotTool: Pivot restored to original position for '{obj}' at {rp}")


# The Widget/Window information to make the function pop up in Maya
class PivotToolWidget(MayaWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pivot Tool")
        self.tool = PivotTool()

        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.masterLayout.addWidget(QLabel("Select one or more objects, then use the options below:"))

        self.masterLayout.addWidget(self._MakeDivider())

        self.masterLayout.addWidget(self._MakeSectionLabel("Reset to World Origin"))
        self.masterLayout.addWidget(QLabel("Moves the pivot of each selected object to (0, 0, 0)."))

        self.resetToWorldBtn = QPushButton("Reset Pivot to World Origin")
        self.resetToWorldBtn.clicked.connect(self.ResetToWorldBtnClicked)
        self.masterLayout.addWidget(self.resetToWorldBtn)

        self.masterLayout.addWidget(self._MakeDivider())

        self.masterLayout.addWidget(self._MakeSectionLabel("Reset to Original Position"))
        self.masterLayout.addWidget(
            QLabel("1. Select object(s) before moving their pivots.\n"
                   "2. Click 'Store Pivots' to save their current positions.\n"
                   "3. Later, click 'Restore Pivots' to return to those positions."))

        self.storePivotsBtn = QPushButton("Store Pivots")
        self.storePivotsBtn.clicked.connect(self.StorePivotsBtnClicked)
        self.masterLayout.addWidget(self.storePivotsBtn)

        self.restorePivotsBtn = QPushButton("Restore Pivots to Original Position")
        self.restorePivotsBtn.clicked.connect(self.RestorePivotsBtnClicked)
        self.masterLayout.addWidget(self.restorePivotsBtn)

        self.storedLabel = QLabel("Stored: None")
        self.masterLayout.addWidget(self.storedLabel)

    def _MakeSectionLabel(self, text):
        label = QLabel(f"  {text}")
        label.setStyleSheet("font-weight: bold; background-color: #3a3a3a; padding: 3px;")
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return label

    def _MakeDivider(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def ResetToWorldBtnClicked(self):
        self.tool.ResetPivotToWorldOrigin()

    def StorePivotsBtnClicked(self):
        self.tool.StorePivotPositions()
        storedNames = list(self.tool.storedPivots.keys())
        if storedNames:
            self.storedLabel.setText(f"Stored: {', '.join(storedNames)}")
        else:
            self.storedLabel.setText("Stored: None")

    def RestorePivotsBtnClicked(self):
        self.tool.ResetPivotToOriginalPosition()

    # Widget hash / address for the widget itself
    def GetWidgetHash(self):
        return "7c68f58ed9cc12da49f04015613f735dafa45c44aeb4f8ea5c4e2e9f40d47d71"

# Makes it activate
def Run():
    pivotToolWidget = PivotToolWidget()
    pivotToolWidget.show()

Run()