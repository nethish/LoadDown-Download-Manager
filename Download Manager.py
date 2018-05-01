from tkinter import *
import requests
from tkinter import filedialog
from tkinter import messagebox
import _thread as thread
import threading
from threading import Thread as TT
MAX_SIZE = 10**9
from tkinter import ttk
from subprocess import Popen

lock = threading.Lock()

class DownloadObject:
    def __init__(self,url,id):
        self.url = url
        details = self.checkurl(url)
        self.exist = True
        self.name = ''

        if not details[0]:
            self.exist = False
        
        self.done = 0
        self.size = details[1]
        self.content_type = details[2]
        self.http_response = details[3]
        self.id = id

    def checkurl(self,url):
        if not url:
            return [False,0,0,0]

        try:
            r = requests.head(url,allow_redirects = True)
        except:
            return [False,0,0,0]
        
        head = r.headers
        
        try :
            size = float(head['content-length'])
        except:
            return [False,0,0,head]
        
        return [True,size,head['Content-Type'],head]

    def __del__(self):
        del self.url


class Idm(Frame):
    global DOWNLOADS
    DOWNLOADS = []

    def __init__(self,master):
        Frame.__init__(self,master)
        self.grid()
        self.master.title('IDM')
        self.master.resizable(False,False)
        self.master.geometry('500x500+600+320')
        self.createWidgets()

    def createWidgets(self):
        self.path = 'C:\\'
        self.url_label = Label(self,text = ' URL Here >> ',fg = 'green',font = ("hobo std",10,'bold'),width = 15,height = 5)
        self.url_label.grid(row = 0,column = 0)
        self.link = Entry(self,font = ("hobo std",10,'italic'),width = 45)
        
        self.link.insert(0,'URL')
        self.link.grid(row = 0,column = 1,columnspan = 1)
        self.start_button = Button(self,text = 'DOWNLOAD',command = self.start,width = 25,bg = 'grey',fg = 'black',font = ("hobo std",10,'bold'))
        self.start_button.grid(row = 1,column = 0,columnspan = 3)
        
        self.quit_button = Button(self,text = 'Quit',bg = 'red',fg = 'white',font = ("hobo std",10,'italic'),command = self.quit,width = 10)
        self.quit_button.grid(row = 1)
        option_list = ['Threads - 1','Threads - 2','Threads - 3','Threads - 4']
        self.threads = '1'
        
        # self.disppath = Label(self,text=self.path)
        # self.disppath.grid(row=1)

        temp = StringVar(self)
        temp.set('Threads - 1')
        self.thread_widget = OptionMenu(self,temp,*option_list,command = self.setThreads)
        self.thread_widget.grid(row = 2,column = 0)
        
        self.progress = []
        for i in range(4):
            self.progress.append(ttk.Progressbar(self, orient="horizontal",length=200, mode="determinate"))
            self.progress[i].grid(row=4+i,column=1,pady=15)

        color = ['green' , 'blue' , 'red' , 'orange']
        functions = [self.openFile1,self.openFile2,self.openFile3,self.openFile4]

        self.download_labels = []
        for i in range(4):
            self.download_labels.append(Button(self, text = str(i+1),bg = color[i] , width = 20 , 
                                        command = functions[i]))
            self.download_labels[i].grid(row=4+i,column=0)

        self.progress_select = [0,0,0,0]
        self.format = ['B','KB','MB','GB','TB']
        self.count = 1
        self.downlaod_paths = []
        for i in range(4):
            self.downlaod_paths.append('C:\\')


    def openFile1(self):
        Popen('explorer '+self.downlaod_paths[0])
    def openFile2(self):
        Popen('explorer '+self.downlaod_paths[1])
    def openFile3(self):
        Popen('explorer '+self.downlaod_paths[2])
    def openFile4(self):
        Popen('explorer '+self.downlaod_paths[3])

    def setThreads(self,threads):
        self.threads = threads[-1]

    def startDownload(self,object,path,start,end,ithread,progress_select,ilock):
        ilock.acquire()

        head  =  {'Range': 'bytes = %d-%d' % (start, end)}
        try:
            r = requests.get(object.url,headers = head,stream = True,allow_redirects = True)
        except:
            ilock.release()
            return False
        
        with open(path,'r+b') as new_file:
            new_file.seek(start)
            for chunk in r.iter_content(chunk_size = 1024):
                object.done += len(chunk)
                self.progress[progress_select]["value"] = object.done
                new_file.write(chunk)
        
        ilock.release()
        return True

    def selectPath(self):
        temp = filedialog.askdirectory()
        if temp:
            self.path = temp

    def start(self):
        url = self.link.get()
        if not url:
            self.link.insert(0,'Not a Valid URL')
            return False
        DOWNLOADS.append(thread.start_new_thread(self.DownloadObject,(url,)))

    def DownloadObject(self,url):
        lock.acquire()
        object = DownloadObject(url,self.count)
        self.count += 1
        if not object.exist:
            messagebox.showinfo(title = 'Sorry',message = "No Data Found or Request Timed out")
            self.count -= 1
            lock.release()
            return False
        
        size = object.size
        form = 0
        
        for i in range(1,5):
            if size//1024**i > 0:
                form = i
        
        forma = self.format[form]   
        downld = messagebox.askquestion(title = 'DownloadObject',
                                        message = 'Proceed DownloadObject ?\nSize = %.2f %s\nType = %s'%(size/1024**form,forma,object.content_type)
                                        )
        if downld  ==  'no':
            self.count -= 1
            lock.release()
            return False
        
        file_types = [('All files', '.*'), ('Text files', '.txt')]
        typ = ''
        typ = object.content_type.split('/')[-1] 

        file_name = 'Newfile.'+typ
        options = {'initialfile' : file_name}
        options['initialdir'] = self.path
        options['filetypes'] = file_types

        path = filedialog.asksaveasfile(mode = 'w',**options)
        if not path:
            self.count -= 1
            lock.release()
            return False
        
        absolute_path = path.name
        file_name = absolute_path.split('/')[-1]
        file_path = "/".join(absolute_path.split('/')[:-1])
        
        if self.count >= 4:
            messagebox.showinfo(title = 'Sorry',message = "MAX DOWNLOADS REACHED")
            lock.release()
            self.count -= 1
            return False

        progress_select = 0
        for i in range(4):
            if not self.progress_select[i]:
                progress_select = i
                self.progress_select[i] = True
                break

        self.downlaod_paths[progress_select] = file_path
        threads = []
        parts = int(self.threads)
        # self.DownloadObjectS.append([False]*parts)
        
        object.name = file_name
        split_size = int(object.size//parts)
        self.progress[progress_select]["maximum"] = object.size
        self.progress[progress_select]["value"] = 0
        self.download_labels[progress_select].config(text = object.name)

        locks = [0]*parts
        for i in range(parts):
            locks[i] = threading.Lock()

        for i in range(parts):
            s = i*split_size
            e = s+split_size
            if i  ==  parts - 1:
                e = object.size
            threads.append(TT(target = self.startDownload,args = (object,absolute_path,s,e,i,progress_select,locks[i])))
        
        lock.release()
        for i in range(parts):
            threads[i].start()

        for i in range(parts):
            threads[i].join()

        return self.postDownload(object,progress_select,locks)

    def postDownload(self,object,progress_select,locks):
        for i in range(len(locks)):
            locks[i].acquire()
            locks[i].release()
        
        del locks

        self.progress_select[progress_select] = False
        self.count -= 1
        if object.size == object.done:
            return True
        
        else:
            object.done = 0
            retry = messagebox.askquestion(title = 'Download Unsuccessful',message = object.name+'\nRetry ?')
            if retry  ==  'no':
                return False
            else:
                return self.DownloadObject(object.url)
        return True

    def quit(self):
        flag = messagebox.askyesnocancel(title = 'WHAT',message = 'Quit ?')
        if flag:
            self.master.destroy()
        return

if __name__ == '__main__':
    root = Tk()
    app = Idm(root)
    app.mainloop()

# https://www.python.org/static/community_logos/python-logo-master-v3-TM.png


