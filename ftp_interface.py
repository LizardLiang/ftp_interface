# -- coding: utf-8 --
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
from tkinter import Canvas
from ftplib import FTP
import pathlib

folders = []
files = []
filelist = []

# get current working directory
path = pathlib.Path(__file__).parent.absolute()

# initialize FTP
ftp = FTP()
window = tk.Tk()


def download_ftp(name):
    # 先記錄原本的路徑在哪
    filename = name
    if name in files:
        # 如果有在檔案列表內才下載
        res = ftp.retrbinary('RETR %s' % filename, open(
            str(path) + '\\' + filename, 'wb').write)
        if '226' in res:
            messagebox.showinfo("提示", "已下載檔案")
        else:
            messagebox.showinfo("提示", "檔案下載失敗")


def upload_ftp():
    filename = filedialog.askopenfilename(initialdir="/", title="Select file")
    ftp_file_name = filename.split('/')
    res = ftp.storbinary(
        "STOR " + ftp_file_name[len(ftp_file_name) - 1], open(filename, 'rb'))
    ftp_refresh()
    if '226' in res:
        messagebox.showinfo("提示", "已上傳檔案")
    else:
        messagebox.showinfo("提示", "檔案上傳失敗")


def del_ftp(name):
    res = ''
    if name in files:
        res = ftp.delete(name)
    elif name in folders:
        res = ftp.rmd(name)
    ftp_refresh()
    if '250' in res:
        messagebox.showinfo('提示', '刪除 ' + name + ' 成功')
    else:
        messagebox.showinfo('提示', '刪除 ' + name + ' 失敗')


def get_select_item(evt):
    item_name = lb.get(lb.curselection())
    # 如果選的東西是資料夾 進入資料夾
    if item_name in folders or item_name == '..':
        get_next_dir(item_name)
    elif item_name in files:
        download_ftp(item_name)


def set_path(tk, p_label):
    global path
    new_path = filedialog.askdirectory(initialdir=path, title="Select file")
    # if new path has been selected
    if new_path != '':
        path = new_path
    p_label.configure(text=path)


def search_init(name):
    if search_file(name) == False:
        messagebox.showerror("提示", "找不到檔案")


def search_file(name):
    found = False
    # 列出所有的檔案包括資料夾
    dir_list = ftp.nlst()
    # 如果沒有找到檔案
    if name not in dir_list:
        for dir in dir_list:
            # 進入下一個資料夾
            try:
                ftp.cwd(dir)
                found = search_file(name)
                # 回到上一個資料夾
                ftp.cwd('..')
            except:
                None
            # 傳回得到的結果
            if found == True:
                return found

        return found
    else:
        # 如果找到就下載
        ftp.retrbinary('RETR %s' % name, open(
            str(path) + '\\' + name, 'wb').write)
        found = True
        return found


# initialize tkinter
window.title("ftp_client")
window.geometry('800x800')
window.configure(background='white')
right_frame = tk.Frame(window)
right_frame.pack(side=tk.RIGHT)
left_frame = tk.Frame(window)
left_frame.pack(side=tk.LEFT)

d_button = tk.Button(right_frame, text="下載", width=32,
                     height=2, fg='red', command=lambda: download_ftp(lb.get(lb.curselection())),
                     font=font.Font(size=10))
u_button = tk.Button(right_frame, text="上傳", width=32,
                     height=2, fg='red', command=lambda: upload_ftp(), font=font.Font(size=10))
p_label = tk.Label(right_frame, text=path, width=32,
                   height=2, font=font.Font(size=10))
search_entry = tk.Entry(right_frame, text=path,
                        width=32, font=font.Font(size=10))
p_button = tk.Button(right_frame, text="設定儲存路徑", width=32,
                     height=2, fg='red', command=lambda: set_path(tk, p_label), font=font.Font(size=10))
del_button = tk.Button(right_frame, text="刪除", width=32,
                       height=2, fg='red', command=lambda: del_ftp(lb.get(lb.curselection())),
                       font=font.Font(size=10))
new_dir_button = tk.Button(right_frame, text="新增資料夾", width=32,
                           height=2, fg='red', command=lambda: name_dir(), font=font.Font(size=10))
search_button = tk.Button(right_frame, text="搜尋", width=32,
                          height=2, fg='red', command=lambda: search_init(search_entry.get()),
                          font=font.Font(size=10))

d_button.pack(side=tk.TOP)
u_button.pack()
del_button.pack()
new_dir_button.pack()
search_entry.pack(ipady=4)
search_button.pack()
p_button.pack()
p_label.pack()
lb = tk.Listbox(left_frame, width=60, height=40, font=font.Font(size=30))
lb.bind('<Double-Button>', get_select_item)
lb.pack()


def ftp_init():
    # to initialize a ftp client setting
    # and connect to server on 203.75.195.122:21
    # login in as administrator
    # print if fail on initializing
    ftp.set_debuglevel(0)
    # 這樣才可以用中文
    ftp.encoding = 'utf-8'
    ftp.connect("203.75.190.122", 21)
    ftp.login("administrator", "12437181")
    welcomemsg = ftp.getwelcome()

    if "220" not in welcomemsg:
        messagebox.showerror("提示", "無法連線到FTP伺服器")

    lb.insert(0, '..')
    filelist = ftp.nlst()

    for dir in filelist:
        lb.insert("end", dir)
        is_dir(dir)


def ftp_refresh():
    lb.delete(0, 'end')
    is_dir_init()
    lb.insert(0, '..')
    filelist = ftp.nlst()

    for dir in filelist:
        lb.insert("end", dir)
        is_dir(dir)


def is_dir_init():
    folders.clear()
    files.clear()


def is_dir(name):
    current = ftp.pwd()
    try:
        ftp.cwd(name)
        ftp.cwd(current)
        folders.append(name)
    except:
        files.append(name)


def get_next_dir(name):
    lb.delete(0, 'end')
    is_dir_init()
    ftp.cwd(name)
    file_list = ftp.nlst()

    lb.insert(0, '..')
    for dir in file_list:
        lb.insert("end", dir)
        is_dir(dir)


def name_dir():
    dialog = tk.Tk()
    dialog.title('新資料夾名稱')
    dialog.geometry('250x150')
    #can = Canvas(dialog, height=75, width=125)
    #can.place(relx=0.5, rely=0.5, anchor='center')
    n_entry = tk.Entry(dialog, width=20, font=font.Font(size=30))
    n_button = tk.Button(dialog, text='新增', height=2, width=10,
                         command=lambda: make_dir(dialog, n_entry.get()), font=font.Font(size=30))
    n_entry.pack(pady=20, ipady=6)
    n_button.pack()
    dialog.mainloop()


def make_dir(dialog, name):
    dialog.destroy()
    res = ftp.mkd(name)
    ftp_refresh()


if __name__ == "__main__":
    ftp_init()
    pass

window.mainloop()
