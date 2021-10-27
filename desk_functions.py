from PySide2.QtWidgets import QMessageBox

def myMsgBox(text, title="Message Box Information", icon=QMessageBox.Information, buttons=QMessageBox.Ok):
    msgBox = QMessageBox()
    msgBox.setText(text)
    msgBox.setWindowTitle(title)
    msgBox.setStandardButtons(buttons)
    msgBox.setIcon(icon)  # Information , Question and warning

    return msgBox.exec_()

# myMsgBox("No Internet Connection", title='Check Network', icon=QMessageBox.Warning)