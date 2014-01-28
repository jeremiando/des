from PyQt4 import QtGui as q
from PyQt4.QtCore import QDate
# nama class yang dibuat menggunakan qt designer
from windows import Ui_DataExplorer, Ui_InsertDialog, Ui_ConnForm
import sqlalchemy
import sys


class ConDialog(q.QDialog, Ui_ConnForm):
    def __init__(self, parent):
        q.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.connBtn.clicked.connect(self.checkDBCon)

    def checkDBCon(self):
        user = self.userInput.text()
        passwd = self.passwdInput.text()
        host = self.hostInput.text()
        db = self.dbInput.text()
        koneksi = 'postgresql://%s:%s@%s/%s' % (user, passwd, host, db)
        db = sqlalchemy.create_engine(koneksi)
        parent = self.parent()

        try:
            parent.con = db.connect()
        except:
            msg = 'Connection Failed :( , Check Your Database Configuration ...'
        else:
            msg = 'Connected :) ...'
            parent.db = db
            parent.setActive()
            parent.showAll()

        q.QMessageBox.information(self, 'NOTIFICATION', msg)
        self.close()



class InputDialog(q.QDialog, Ui_InsertDialog):
    def __init__(self, parent, dbcon, data=None):
        q.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.con = dbcon

        # pada saat tombol create ditekan
        if not data:
            self.insertBtn.clicked.connect(self.insertRecord)
        else:
            self.insertBtn.clicked.connect(self.editRecord)
            self.insertBtn.setText('Edit')
            self.data = data
            self.setText()

    def getAllText(self):
        params = {
            'alamat': str(self.alamatInput.toPlainText()),
            'tgl_lahir': str(self.tglLhrInput.text()),
            'nama': str(self.namaInput.text()),
            'kelamin': str(self.kelaminInput.currentText())
        }

        params['kelamin'] = True if params['kelamin'] == 'Male' else False

        return params

    def insertRecord(self):

        params = self.getAllText()

        query = "INSERT INTO biodata(nama,tgl_lahir, kelamin, alamat) values(%(nama)s, %(tgl_lahir)s, %(kelamin)s, %(alamat)s)"

        try:
            self.con.execute(query, **params)
        except:
            msg = 'Fail To Insert'
        else:
            msg = 'Record Inserted ...'
            self.parent().showAll()

        q.QMessageBox.information(self, 'NOTIFICATION', msg)
        self.close()

    def setText(self):
        print self.data
        id, nama, tgl_lahir, kelamin, alamat = self.data
        tgl_lahir = QDate.fromString(tgl_lahir, 'yyyy-MM-dd')
        kelamin = 1 if kelamin == 'Male' else 0

        self.namaInput.setText(nama)
        self.alamatInput.setText(alamat)
        self.tglLhrInput.setDate(tgl_lahir)
        self.kelaminInput.setCurrentIndex(kelamin)


    def editRecord(self):
        params = self.getAllText()
        params['id'] = int(self.data[0])

        query = "UPDATE biodata SET nama=%(nama)s, tgl_lahir=%(tgl_lahir)s, kelamin=%(kelamin)s, alamat=%(alamat)s WHERE id=%(id)s"

        try:
            self.con.execute(query, **params)
        except:
            msg = 'Fail To Edit'
        else:
            msg = 'Record Edited ...'
            self.parent().showAll()

        q.QMessageBox.information(self, 'NOTIFICATION', msg)
        self.close()



#from PyQt4.QtCore import  QModelIndex

class WindowUtama(q.QMainWindow, Ui_DataExplorer):

    def __init__(self, parent=None):
        q.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.initSignal()
        self.db = None
        self.con = None

    def tesSaya(self):
        print "Hello world"

    def initSignal(self):
        # tombol connect
        self.actionConnection.triggered.connect(self.openConDlg)
        # tombol create record
        self.actionCreate.triggered.connect(self.openCreateDlg)
        # tombol edit
        self.actionEdit.triggered.connect(self.openEditDlg)
        # tombol hapus
        self.actionDelete.triggered.connect(self.deleteRecord)

    def deleteRecord(self, e):
        datas = self.getSelectedRow()
        if not datas:
            q.QMessageBox.information(self, 'Warning', 'You Must Select Data First !!!')
            return

        query = "DELETE FROM biodata WHERE id = %(id)s"
        id = int(datas[0])

        try:
            self.con.execute(query, id=id)
        except:
            msg = 'Failed To Remove'
        else:
            msg = 'Record Removed ...'
            self.showAll()

        q.QMessageBox.information(self, 'NOTIFICATION', msg)



    def openCreateDlg(self, e):
        dlg = InputDialog(self, self.con)
        dlg.setWindowTitle("Create Record")
        dlg.show()

    def openEditDlg(self, e):
        #print self.tableWidget.selectionModel.currentIndex()
        datas = self.getSelectedRow()
        if not datas:
            q.QMessageBox.information(self, 'Warning', 'You Must Select Data First !!!')
            return

        dlg = InputDialog(self, self.con, datas)
        dlg.setWindowTitle("Edit Record")
        dlg.show()

    def getSelectedRow(self):
        datas = [str(x.text()) for x in self.tableWidget.selectedItems()]
        return datas

    def openConDlg(self, e):
        """
        Dialog Database connection
        """
        dlg = ConDialog(self)
        dlg.show()

    def setActive(self):
        self.actionCreate.setEnabled(True)
        self.actionDelete.setEnabled(True)
        self.actionEdit.setEnabled(True)

    def showAll(self):
        sql = "SELECT * FROM biodata"
        results = self.con.execute(sql).fetchall()
        jumlah = len(results)
        self.tableWidget.setRowCount(jumlah)

        for row in range(jumlah):
            result = results[row]
            for col in range(len(result)):
                content = result[col]
                if type(content) == bool:
                    content = "Male" if content else "Female"

                self.tableWidget.setItem(row, col, q.QTableWidgetItem(str(content)))

# setiap aplikasi qt harus ada QApplication
app = q.QApplication(sys.argv)

window = WindowUtama()
window.show()

# jalankan aplikasi
sys.exit(app.exec_())
