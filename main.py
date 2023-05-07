from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
import GUI
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QFileDialog
import sys
from math import ceil
import re
from urllib.parse import quote
import time

header = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
    Chrome/55.0.2883.87 Safari/537.36'}


class Literature(object):
    #this class has the properties of a literature, including its title, website link, pdf material link, author and abstract
    def __init__(self, id = 0, title = None, link = None, pdf_url = None, author = [], abstract = None, date = None):
        self.id = id
        self.title = title
        self.link = link
        self.pdf_url = pdf_url
        self.author = author #a list to store several authors in one article
        self.abstract = abstract 
        self.date = date

class SearchArxiv(object):
    #this class has the property to store literature datas from search results, and have the function/
    # to search articles on arXiv website for a given question.

    literaturelist = [] #searched papers will be stored in this list as a series of datas with the Literature type

    def __init__(self, quest: str, number: int, ui: GUI.Ui_MainWindow):
        self.quest = quest #the question given by user
        self.number = number
        self.ui = ui

    def printf(self, mes: str):
        self.ui.output.append(mes)
        self.cursot = self.ui.output.textCursor()
        self.ui.output.moveCursor(self.cursot.End)
        GUI.QApplication.processEvents()
 
    def search(self):
        #this function is to search the given number of articles from the website

        #make a get request to the website for search results
        url =  'https://arxiv.org/search/physics?query=' + self.quest +'&searchtype=all&abstracts=show&order=-announced_date_first&size=50'
        #try:
        r = requests.get(url,headers = header)
        #situation when failng to connect to the website
        '''except:
            self.self.printff('cannot connect to the internet')
          return -1'''
        if 200 != r.status_code:
            self.printf('cannot search papers from arXiv')
            return -1
        
        #parse the data with beautifulsoup
        bs = BeautifulSoup(r.content,'html.parser')
    
        paperid, page = 0, 0
        while paperid < self.number:
            flag = 0 #signal variable
            for node in bs.find_all('ol',class_='breathe-horizontal'):
                paperlist = node.find_all('li',class_='arxiv-result')
                for paper in paperlist:
                    flag = 1 #change value when geting results successfully
                    literature = Literature()
                    literature.id = paperid + 1
                    literature.title = paper.find('p',class_='title is-5 mathjax').text.strip()
                    literature.link = (paper.find('p',class_='list-title').find('a'))['href']
                    literature.pdf_url = (paper.find('p',class_='list-title').find('span').find('a'))['href']
                    literature.author = []
                    for author in paper.find('p',class_='authors').find_all('a'):
                        literature.author.append(author.text.strip())
                    literature.abstract = paper.find('p',class_='abstract mathjax').find('span',class_='abstract-full').text.replace('△ Less','').strip()
                    literature.date = paper.find('p',class_='is-size-7').text.strip()[10:].split(';')[0]
                    paperid += 1
                    self.literaturelist.append(literature)
                    if paperid >= self.number: #check if the number of searched articles has reached to its maximun
                        return 1
                    
            if 0 == flag: #condition when there is no more search results
                self.printf('no more results')
                return 1
            page += 1
            url =  'https://arxiv.org/search/physics?query=' + self.quest +'&searchtype=all&abstracts=show&order=-announced_date_first&size=50' + '&start=' + str(50 * page)
        #    try:
            r = requests.get(url,headers = header)
            #situation when failng to connect to the website
            ''' except:
                self.self.printf('cannot connect to the internet')
                return -1
            '''
            if 200 != r.status_code: #condition when failed to connect to the website
                self.printf('Some unexpected mistakes happened when searhing from arXiv')
                return 0
            bs = BeautifulSoup(r.content,'html.parser')

            
class SearchPrl(object):

       #this class has the property to store literature datas from search results, and have the function/
    # to search articles on psysical review letters website for a given question.

    literaturelist = [] #searched papers will be stored in this list as a series of datas with the Literature type

    def __init__(self, quest: str, number: int, ui: GUI.Ui_MainWindow):
        self.quest = quest #the question given by user
        self.number = number
        self.ui = ui

    def printf(self, mes: str):
        self.ui.output.append(mes)
        self.cursot = self.ui.output.textCursor()
        self.ui.output.moveCursor(self.cursot.End)
        GUI.QApplication.processEvents()
 
    def search(self):
        #this function is to search the given number of articles from the website

        #make a get request to the website for search results
        url =  'https://journals.aps.org/search/results?sort=relevance&clauses=' + quote('[{"operator":"AND","field":"all","value":"%s"}]'%(self.quest))
        option = Options()
        option.add_argument('--headless=new')
        #option.headless = True
        option.add_argument('--disable-gpu')
        driver = webdriver.Edge(options=option)
        try:
            driver.get(url)
        #situation when failng to connect to the website
        except(ConnectionRefusedError):
            self.self.printf('cannot connect to the internet')
            return -1
       
        driver.implicitly_wait(5) #wait for the webpage to completely load
        if [] == driver.find_elements(By.ID, 'search-main'):
            self.printf('cannot find any search sesult')
            driver.close()
            return 1
        #ckick to show the abstract
        pluses = driver.find_elements(By.CLASS_NAME, 'fi-plus')
        for plus in pluses:
            plus.click()
        #abstracts= driver.find_elements(By.CLASS_NAME, 'summary')
        #print(len(abstracts))
        #parse the data
        bs = BeautifulSoup(driver.page_source, 'html.parser')

        paperid, page = 0, 0
        while paperid < self.number:
            flag = 0 #signal variable
            for node in bs.find_all('div',class_='large-9 columns search-results ofc-main'):
                paperlist = node.find_all('div',class_='large-9 columns')
                for paper in paperlist:
                    flag = 1 #change value when geting results successfully
                    literature = Literature()
                    literature.id = paperid + 1
                    literature.title = paper.find('h5',class_='title').text.strip()
                    literature.link = 'https://journals.aps.org' + (paper.find('h5',class_='title').find('a'))['href']
                    literature.pdf_url = literature.link.replace('abstract', 'pdf')
                    literature.author = []
                    for author in paper.find('h6',class_='authors').text.replace('and', ',').strip().split(', '):
                        literature.author.append(author.strip())
                    if None != paper.find(class_='summary'):
                        literature.abstract = paper.find(class_='summary').find('p').text.strip()
                    else:
                        literature.abstract = 'no more abstract'

                    literature.date = re.findall('(?<=Published ).*$',paper.find('h6',class_='citation').text.strip())[0]
                    paperid += 1
                    self.literaturelist.append(literature)
                    if paperid >= self.number: #check if the number of searched articles has reached to its maximun
                        driver.close()
                        return 1
                    #i = 0
                    #while i < 20:
                    #    try:
                    #        literature.abstract = paper.find_element(By.CLASS_NAME, 'summary').text
                    #        break
                    #    except:
                    #        print('faled to get information from paper ' + paperid)
                    #    i += 1
            if 0 == flag: #condition when there is no more search results
                self.printf('no more results')
                driver.close()
                return 1
            if paperid >= self.number: #check if the number of searched articles has reached to its maximun
                driver.close()
                return 1
            page += 1
            url =  'https://journals.aps.org/search/results?sort=relevance&clauses=' + quote('[{"operator":"AND","field":"all","value":"%s"}]'%(self.quest)) + '&page=' + str(page + 1)
            driver = webdriver.Edge()
            try:
                driver.get(url)
            #situation when failng to connect to the website
            except(ConnectionRefusedError):
                self.self.printf('cannot connect to the internet')
                driver.close()
                return -1

            
            #click to show the abstract
            pluses = driver.find_elements(By.CLASS_NAME, 'fi-plus')
            for plus in pluses:
                plus.click()
            #parse the data
            bs = BeautifulSoup(driver.page_source, 'html.parser')
        return 1

   #This class helps to connect the search results to the users' UI     
class ResultList(object):
   
    def __init__(self, ui : GUI.Ui_MainWindow):
        self.ui = ui
        self.rows = 12
        self.page = 1
        self.last_page = 1
        self.path = ".\\"
        self.start_id = 0 #the paper_id of the fisrt paper in a particular page
        self.result_number = 0
    
    #print information on the UI
    def printf(self, mes: str):
        self.ui.output.append(mes)
        self.cursot = self.ui.output.textCursor()
        self.ui.output.moveCursor(self.cursot.End)
        GUI.QApplication.processEvents()

    #This function is to search the article when the search button is clicked
    def search_results(self):
        quest = self.ui.lineEdit_search.text().strip()
        if None == quest:
            return -1
        number = int(self.ui.lineEdit_searchItems.text().strip())
        self.printf('searching...')
        if 0 == self.ui.comboBox_search_on.currentIndex():
            self.papers = SearchArxiv(quest,number,self.ui) #where papers is a class,has a list proeprty: literaturelist[] to store the paper class
            self.papers.search()
            self.result_number = len(self.papers.literaturelist)
            self.last_page = ceil(self.result_number / self.rows) #to find the final page
        elif 1 == self.ui.comboBox_search_on.currentIndex():
            self.papers = SearchPrl(quest,number,self.ui) #where papers is a class,has a list proeprty: literaturelist[] to store the paper class
            self.papers.search()
            self.result_number = len(self.papers.literaturelist)
            self.last_page = ceil(self.result_number / self.rows) #to find the final page
        self.printf('there are ' + str(self.result_number) + ' results')

    #show the search results on the UI table
    def show_results(self):
        self.clear()
        ui.lineEdit_page.setText('%s/%s'%(self.page,self.last_page)) #change the pagination
        #self.printf the search result on the ui table
        self.ui.table_search.clearContents
        self.start_id = self.rows * (self.page - 1)
        final_row = self.rows if self.page < self.last_page else self.result_number - self.start_id
        for row in range(0,final_row):
            id = self.start_id + row
            paper = self.papers.literaturelist[id]
            self.ui.table_search.setItem(row, 0, QTableWidgetItem(paper.title))
            self.ui.table_search.setItem(row, 1, QTableWidgetItem(paper.date))
            self.ui.table_search.setItem(row, 3, QTableWidgetItem(paper.abstract))
            self.ui.table_search.setItem(row, 4, QTableWidgetItem(paper.link))
            for author in paper.author:
                self.ui.table_search.setItem(row, 2, QTableWidgetItem(author + ','))

    #functions to help to turn a page
    def next_page(self):
        if self.page != self.last_page:
            self.page += 1
            
            self.show_results()
    
    def previous_page(self):
        if self.page != 1:
            self.page -= 1
            self.show_results()
    #clear the search results on the UI table, but results are still stored in the class
    def clear(self):
        for row in range(0,self.rows):
            self.ui.table_search.setItem(row, 0, QTableWidgetItem(''))
            self.ui.table_search.setItem(row, 1, QTableWidgetItem(''))
            self.ui.table_search.setItem(row, 2, QTableWidgetItem(''))
            self.ui.table_search.setItem(row, 3, QTableWidgetItem(''))
            self.ui.table_search.setItem(row, 4, QTableWidgetItem(''))

    #the following function is to download the pdf file
    #change the download path
    def set_download_path(self):
        self.path = QFileDialog.getExistingDirectory(None, "Please choose the download path", self.path)
        self.printf('download path has been successufly set as '+ self.path)

    def download(self,literature:Literature):
        #try:
        r = requests.get(literature.pdf_url,headers = header)
        #except:
        #    self.printf('request to download' + str(literature.title) +'failed,cannot connect to the internet')
        #    return -1
        if 200 != r.status_code:
            self.printf('request to download' + str(literature.title) +'failed,cannot connect to the internet')
            return -1
        #try:
        self.printf('downloading from ' + literature.pdf_url)
        with open(self.path + str(literature.id) + ',' + literature.title + '.pdf','wb') as f:
            f.write(r.content)
            f.flush() #in case of the file is in the buffer!!
            return 1
       # except:
         #   self.printf('cannot not download' + str(literature.title))
        #    return -1

    def download_all(self):
        if 0 == self.result_number:
            return -1
        self.printf('downloading...')
        for literature in self.papers.literaturelist: #the url of pdfs we need is a property of the paper class
            self.download(literature)
        for row in range(0,self.rows):
            ui.table_pushButton[row].setText('downloaded')
        self.printf('downloading task finished')

    #this function is to download a particular article when you click on the download button
    def click_to_download(self, row: int):
        if self.start_id + row >= self.result_number:
            return 0
        ui.table_pushButton[row].setText('downloading')
        if 1 == self.download(self.papers.literaturelist[self.start_id + row]):
            ui.table_pushButton[row].setText('downloaded')
            self.printf('pdf has been downloaded')
        else:
            ui.table_pushButton[row].setText('download')

    #this function is coming soon
    def look_for_reference(self):
        self.printf('coming soon!')
    
    
#coming soon
class Reference(object):
    
    literaturelist = []
   
if __name__ == "__main__":

    app = GUI.QApplication(sys.argv)
    MainWindow = GUI.QMainWindow()
    ui = GUI.Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    resultlist = ResultList(ui)

    #define connection
    ui.pushButton_search.clicked.connect(lambda: resultlist.search_results())
    ui.pushButton_search.clicked.connect(lambda: resultlist.show_results())
    ui.pushButton_next.clicked.connect(lambda: resultlist.next_page())
    ui.pushButton_previous.clicked.connect(lambda: resultlist.previous_page())
    ui.pushButton_clear.clicked.connect(lambda: resultlist.clear())
    #set download path:
    ui.pushButton_set_path.clicked.connect(lambda: resultlist.set_download_path())
    #download search results:
    ui.pushButton_download_all.clicked.connect(lambda: resultlist.download_all())

    ui.table_pushButton[0].clicked.connect(lambda: resultlist.click_to_download(0))
    ui.table_pushButton[1].clicked.connect(lambda: resultlist.click_to_download(1))
    ui.table_pushButton[2].clicked.connect(lambda: resultlist.click_to_download(2))
    ui.table_pushButton[3].clicked.connect(lambda: resultlist.click_to_download(3))
    ui.table_pushButton[4].clicked.connect(lambda: resultlist.click_to_download(4))
    ui.table_pushButton[5].clicked.connect(lambda: resultlist.click_to_download(5))
    ui.table_pushButton[6].clicked.connect(lambda: resultlist.click_to_download(6))
    ui.table_pushButton[7].clicked.connect(lambda: resultlist.click_to_download(7))
    ui.table_pushButton[8].clicked.connect(lambda: resultlist.click_to_download(8))
    ui.table_pushButton[9].clicked.connect(lambda: resultlist.click_to_download(9))
    ui.table_pushButton[10].clicked.connect(lambda: resultlist.click_to_download(10))
    ui.table_pushButton[11].clicked.connect(lambda: resultlist.click_to_download(11))
    #look for reference
    ui.pushButton_search_references.clicked.connect(lambda: resultlist.look_for_reference())
    MainWindow.show()
    sys.exit(app.exec())





