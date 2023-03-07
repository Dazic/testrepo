from GUI_Search import Ui_Dialog
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QMessageBox, QDialog, QWidget, QGridLayout, QVBoxLayout)
from GUI_Mainwindow import Ui_MainWindow, QDoubleSpinBox, QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QFont
import pymysql, re, sys
import pandas as pd
from Report import Report
from datetime import datetime


class findWindow(QDialog):
    def __init__(self, parent, num):
        super(findWindow, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.show()

        self.ui.pushButton_Find.clicked.connect(self.update_table)
        self.ui.pushButton_Apply.clicked.connect(self.apply)

        self.num = num
        self.parent = parent
        self.conn = parent.conn
        self.li = parent.lineEdit_EtfInfo[self.num]


    def update_table(self):
        self.get_comp_info()
        self.ui.listWidget.clear()
        text = self.ui.lineEdit.text()  # 입력창 단어 가져오기
        re_condition = re.compile(f'.*{text}', re.I)   # 정규식 조건설정(입력단어 포함)


        for idx in self.codes.items():
            if re_condition.match(idx[1]) or re_condition.match(idx[0]):
                if self.ui.comboBox_Category.currentText() == "한국ETF":
                    sql = f"SELECT date FROM daily_price_korea WHERE code = '{idx[0]}' ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
                elif self.ui.comboBox_Category.currentText() == "미국ETF":
                    sql = f"SELECT date FROM daily_price_usa WHERE code = '{idx[0]}' ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
                elif self.ui.comboBox_Category.currentText() == "인덱스":
                    sql = f"SELECT date FROM daily_indices_price WHERE code = '{idx[0]}' ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
                period = pd.read_sql(sql, self.conn)
                period['date'] = period['date'].astype('str')
                start_date = str(period.values[0])[2:-2]
                end_date = str(period.values[-1])[2:-2]
                words = f"({idx[0]}) | {idx[1]} | ({start_date} ~ {end_date})"
                self.ui.listWidget.addItem(words)
        self.ui.listWidget.addItem("-"*70)


    def get_comp_info(self):
        self.codes = {}
        if self.ui.comboBox_Category.currentText() == "한국ETF":
            sql = "SELECT * FROM company_info_korea"      # DB에서 기업코드, 기업명 codes 딕셔너리로 가져오기
        elif self.ui.comboBox_Category.currentText() == "미국ETF":
            sql = "SELECT * FROM company_info_usa"  # DB에서 기업코드, 기업명 codes 딕셔너리로 가져오기
        elif self.ui.comboBox_Category.currentText() == "인덱스":
            sql = "SELECT * FROM indices_info"  # DB에서 기업코드, 기업명 codes 딕셔너리로 가져오기
        krx = pd.read_sql(sql, self.conn)
        for idx in range(len(krx)):
            self.codes[krx['code'].values[idx]] = krx['company'].values[idx]

    def apply(self):
        for i in self.ui.listWidget.selectedItems():
            text = i.text()
        self.li.setText(f"  {text}")
        self.close()


class WindowClass(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.lineEdit_EtfInfo = list(None for i in range(0, 15))
        self.pushButton_FindEtf = list(None for i in range(0,15))
        self.pushButton_Delete = list(None for i in range(0, 15))
        self.spinBox_Ratio = list(0 for i in range(0, 15))

        self.code_N_Ratio = list()
        self.ETF_Count = 1

        self.lineEdit_EtfInfo[0] = self.lineEdit_EtfInfo_1
        self.pushButton_FindEtf[0] = self.pushButton_FindEtf_1
        self.pushButton_Delete[0] = self.pushButton_Delete_1
        self.spinBox_Ratio[0] = self.doubleSpinBox_Ratio_1

        self.pushButton_AddEtf.clicked.connect(self.add_ETF)
        self.pushButton_Delete[0].clicked.connect(lambda: self.sub_ETF(0))
        self.pushButton_FindEtf[0].clicked.connect(self.find_ETF)
        self.pushButton_Backtest.clicked.connect(self.start_Backtest)
        self.lineEdit_EtfInfo[0].textChanged.connect(self.set_Period)


        self.conn = pymysql.connect(host='localhost', user='root',
                                password='', db='ETF', charset='utf8')  # DB 접속
        self.spinBox_Ratio[0].valueChanged.connect(self.sum_spinbox)

    def __del__(self):
        """소멸자: MariaDB 연결 해제"""
        self.conn.close()


    def add_ETF(self):
        font = QFont()
        font.setPointSize(12)
        num = self.ETF_Count + 1

        self.gridLayout_2.addWidget(self.pushButton_AddEtf, num+1, 2, 1, 1) # 추가 버튼

        self.gridLayout_2.addWidget(self.label_TotalRatio, num+2, 3, 1, 1) # 합계 라벨

        self.gridLayout_2.addWidget(self.label_ToralRatioPercent, num+2, 4, 1, 1) # 합계 라벨 퍼센트 표시

        self.label_No_1 = QLabel(self.gridLayoutWidget_2)   # 자산 No
        self.label_No_1.setObjectName(u"label_No_1")
        self.label_No_1.setFont(font)
        self.gridLayout_2.addWidget(self.label_No_1, num, 0, 1, 1)
        self.label_No_1.setText(f"자산{num}")

        self.lineEdit_EtfInfo[self.ETF_Count] = QLineEdit(self.gridLayoutWidget_2)    # 자산 표시창
        self.lineEdit_EtfInfo[self.ETF_Count].setObjectName(f"lineEdit_EtfInfo_{num}")
        self.lineEdit_EtfInfo[self.ETF_Count].setEnabled(False)
        self.lineEdit_EtfInfo[self.ETF_Count].setFont(font)
        self.lineEdit_EtfInfo[self.ETF_Count].setText("검색/설정 버튼으로 자산을 추가하세요.")
        self.gridLayout_2.addWidget(self.lineEdit_EtfInfo[self.ETF_Count], num, 1, 1, 1)
        self.lineEdit_EtfInfo[self.ETF_Count].textChanged.connect(self.set_Period)

        self.pushButton_FindEtf[self.ETF_Count] = QPushButton(self.gridLayoutWidget_2)    # 검색/설정 버튼
        self.pushButton_FindEtf[self.ETF_Count].setObjectName(f"pushButton_FindEtf_{num}")
        self.pushButton_FindEtf[self.ETF_Count].setFont(font)
        self.pushButton_FindEtf[self.ETF_Count].setText("검색/설정")
        self.gridLayout_2.addWidget(self.pushButton_FindEtf[self.ETF_Count], num, 2, 1, 1)
        self.pushButton_FindEtf[self.ETF_Count].clicked.connect(lambda : self.find_ETF(num-1))

        self.spinBox_Ratio[self.ETF_Count] = QDoubleSpinBox(self.gridLayoutWidget_2)    # 스핀박스
        self.spinBox_Ratio[self.ETF_Count].setObjectName(f"spinBox_Ratio_{num}")
        self.spinBox_Ratio[self.ETF_Count].setFont(font)
        self.spinBox_Ratio[self.ETF_Count].setMaximum(100)
        self.gridLayout_2.addWidget(self.spinBox_Ratio[self.ETF_Count], num, 3, 1, 1)
        self.spinBox_Ratio[self.ETF_Count].valueChanged.connect(self.sum_spinbox)

        self.label_Per_1 = QLabel(self.gridLayoutWidget_2)  # 퍼센트 표시
        self.label_Per_1.setObjectName(u"label_Per_1")
        self.label_Per_1.setFont(font)
        self.label_Per_1.setText("%")
        self.gridLayout_2.addWidget(self.label_Per_1, num, 4, 1, 1)

        self.pushButton_Delete[self.ETF_Count] = QPushButton(self.gridLayoutWidget_2) # 삭제버튼
        self.pushButton_Delete[self.ETF_Count].setObjectName(f"pushButton_Delete{num}")
        self.pushButton_Delete[self.ETF_Count].setFont(font)
        self.pushButton_Delete[self.ETF_Count].setText("삭제")
        self.gridLayout_2.addWidget(self.pushButton_Delete[self.ETF_Count], num, 5, 1, 1)
        self.pushButton_Delete[self.ETF_Count].clicked.connect(lambda : self.sub_ETF(num-1))

        self.ETF_Count += 1

    def sub_ETF(self, num):
        if self.ETF_Count > 1:
            if self.ETF_Count == num + 1:
                pass
            else:
                for line in range(num, self.ETF_Count-1):
                    self.lineEdit_EtfInfo[line].setText(self.lineEdit_EtfInfo[line+1].text())
                    self.spinBox_Ratio[line].setValue(self.spinBox_Ratio[line+1].value())
                print(f"num = {num}, ETF_Count = {self.ETF_Count}")
            for lastLine in range(0, 6):
                self.gridLayout_2.itemAtPosition(self.ETF_Count, lastLine).widget().deleteLater()

            self.ETF_Count -= 1
            self.set_Period()

    def sum_spinbox(self):
        total = 0
        for i in range(self.ETF_Count):
            total += self.spinBox_Ratio[i].value()
        self.label_TotalRatio.setText(str(total))
        if total != 100:
            self.label_TotalRatio.setStyleSheet(u"color: rgb(255, 0, 0)")
        else:
            self.label_TotalRatio.setStyleSheet(u"color: rgb(0, 0, 0)")

    def find_ETF(self, num):
        findWindow(self, num)


    def start_Backtest(self):
        # 백테스트 기간 / 거래수수료 설정
        self.start_date = self.dateEdit_StartDate.date().toString('yyyy-MM-dd')  # 시작 날짜
        self.end_date = self.dateEdit_EndDate.date().toString('yyyy-MM-dd')  # 끝 날짜
        # 종목별 배분비율 데이터프레임 생성
        self.code_N_Ratio = list()  #   리스트 초기화
        for num in range(0, self.ETF_Count):        # ETF 코드, 투자비율 추출
            code = self.lineEdit_EtfInfo[num].text().split('|')
            code = code[0].strip(' ()')
            self.code_N_Ratio.append([code,
                              self.spinBox_Ratio[num].value()])
        self.code_N_Ratio = pd.DataFrame(self.code_N_Ratio, columns=["Code", "Asset_Ratio"])
        self.code_N_Ratio.set_index('Code', inplace=True)
        print(self.code_N_Ratio)


        # DB 생성
        self.ETF_Price = self.makeDB("MyAsset", "code", self.code_N_Ratio.index.to_list())
        self.Index_KOSPI = self.makeDB("Index", "code", ["Index_KS11"])
        self.Index_SnP500 = self.makeDB("Index", "code", ["Index_US500"])

        Report(self)

    def set_Period(self):
        start = list()
        end = list()

        for num in range(0, self.ETF_Count):
            start.append(datetime.strptime(self.lineEdit_EtfInfo[num].text()[-24: -14], '%Y-%m-%d'))
            end.append(datetime.strptime(self.lineEdit_EtfInfo[num].text()[-11:-1], '%Y-%m-%d'))

        self.dateEdit_StartDate.setDate(start[0])
        self.dateEdit_EndDate.setDate(end[0])
        for start in start:
            if self.dateEdit_StartDate.date()  <= start:
                    self.dateEdit_StartDate.setDate(start)
        for end in end:
            if self.dateEdit_EndDate.date() <= end:
                    self.dateEdit_EndDate.setDate(end)

    def makeDB(self, Type, Tablecolumn, NameList):
        index_SW = False
        DB = pd.DataFrame({"date": []})
        if Type == 'Index':
            for name in (NameList):
                sql = f"SELECT date, close FROM daily_indices_price WHERE ({Tablecolumn} = '{name}')" \
                      f" AND (date >= '{self.start_date}' AND date <= '{self.end_date}') ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
                period = pd.read_sql(sql, self.conn)
                period.rename(columns={'close': name}, inplace=True)
                DB = pd.merge(DB, period, on='date', how='outer')
        if Type == 'MyAsset':
            # DB에서 환율 불러오기
            sql = f"SELECT date, close FROM daily_indices_price WHERE (code = 'Index_USD/KRW')" \
                  f" AND (date >= '{self.start_date}' AND date <= '{self.end_date}') ORDER BY date ASC"
            period = pd.read_sql(sql, self.conn)
            period.rename(columns={'close': 'Exchange_Dollar'}, inplace=True)
            DB = pd.merge(DB, period, on='date', how='outer')
            for name in NameList:
                if len(name) > 6:
                    sql = f"SELECT date, close FROM daily_indices_price WHERE ({Tablecolumn} = '{name}')" \
                          f" AND (date >= '{self.start_date}' AND date <= '{self.end_date}') ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
                    index_SW = True
                elif  64 <= ord(name[0]) <= 90:  # 아스키코드 64~90(A-Z) 중 존재한다면(미국 티커)
                    sql = f"SELECT date, close FROM daily_price_usa WHERE ({Tablecolumn} = '{name}')" \
                          f" AND (date >= '{self.start_date}' AND date <= '{self.end_date}') ORDER BY date ASC"
                else:  # 그렇지 않다면 (한국 코드값, 한국은 숫자이기 때문)
                    sql = f"SELECT date, close FROM daily_price_korea WHERE ({Tablecolumn} = '{name}')" \
                          f" AND (date >= '{self.start_date}' AND date <= '{self.end_date}') ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
                period = pd.read_sql(sql, self.conn)
                period.rename(columns={'close': name}, inplace=True)
                DB = pd.merge(DB, period, on='date', how='outer')
                if 64 <= ord(name[0]) <= 90 and self.checkBox_Currency.isChecked():  # 아스키코드 64~90(A-Z) 중 존재한다면(미국 티커)
                    DB = DB.dropna()
                    DB = DB.sort_values(by='date', ascending=True)
                    # DB = DB.sort_values(by='date', ascending=True).fillna(method='ffill')
                    # DB = DB.dropna()
                    DB[name] = DB[name] * DB['Exchange_Dollar']
                    DB[name] = DB[name].round(0).astype(int)
            DB.drop('Exchange_Dollar', axis=1, inplace=True)
            #DB.to_excel('Asset.xlsx')
        DB['date'] = pd.to_datetime(DB['date'])  # date 컬럼 데이터타임프레임으로 변경
        DB.set_index('date', inplace=True)
        DB = DB.sort_index().fillna(method='ffill')
        if index_SW == True:
            DB = (DB*1000) / DB.iloc[0]
            DB.to_excel('DB.xlsx')


        return DB


    def makeDB_Backup(self, TableName, Tablecolumn, NameList):
        DB = pd.DataFrame({"date": []})
        for name in (NameList):
            sql = f"SELECT date, close FROM {TableName} WHERE ({Tablecolumn} = '{name}')" \
                  f" AND (date >= '{self.start_date}' AND date <= '{self.end_date}') ORDER BY date ASC"  # 오름차순정렬 DB자료 수집
            period = pd.read_sql(sql, self.conn)
            period.rename(columns={'close': name}, inplace=True)
            DB = pd.merge(DB, period, on='date', how='outer')
        DB['date'] = pd.to_datetime(DB['date'])  # date 컬럼 데이터타임프레임으로 변경
        DB.set_index('date', inplace=True)
        return DB


app = QApplication(sys.argv)
mainWindow = WindowClass()
mainWindow.show()
sys.exit(app.exec())

## 개선해야 할것.
# 1. 인덱스추가 : KIS 10Y KTB Index (Total return Index, 총수익지수) - 국고채 10년
#                       S&P 10-year US Treasury Note Futures KRW - 미국채 10년
# 인덱스를 추가하면, 기존의 한국/미국 주식 나누는 기준때문에 에러가 난다.
# 한국인덱스, 미국인덱스 DB를 나눠서 받아 정리하자.
# 환율 무시 조건 넣자