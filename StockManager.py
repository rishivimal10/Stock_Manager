import tkinter as tk
from tkinter import ttk
import requests
import json
import sys
import os

import sqlite3
import api_requests

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.animation as animation
from matplotlib import style


LARGE_FONT = ("Verdana", 12)
NORM_FONT = ("Arial", 10)
url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=VGRO.TO&interval=5min" \
      "&apikey=DBBCEP6J972FNU4I"
style.use("ggplot")


def graph_page():
    root = tk.Tk()
    root.wm_title("Graph Page")

    f = plt.figure()
    a = f.add_subplot(111)

    def animate(i):
        response = requests.get(url)
        data = json.loads(response.text)
        stock = data['Meta Data']['2. Symbol']
        data = data['Time Series (5min)']
        time_list = list(data)
        time_list.reverse()
        print(time_list)

        price_list = []

        for time in time_list:
            price_list.append(data[time]['4. close'])

        price_list.reverse()

        a.clear()
        a.plot(time_list, price_list)

        title = stock+"'s Price Chart\nLast Price: " + str(price_list[99])
        a.set_title(title)

    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root.ani = animation.FuncAnimation(f, animate, interval=20000)
    root.geometry('1280x700')
    root.mainloop()


def restart ():
    python = sys.executable
    os.execl(python, python, *sys.argv)


def search():

    search_page = tk.Tk()
    search_page.wm_title("Search Page")

    label = ttk.Label(search_page, text="Search Stocks", font=LARGE_FONT)
    label.pack(pady=10, padx=10)

    search_box = ttk.Entry(search_page, width=50)
    search_box.pack()

    search_button2 = ttk.Button(search_page, text="Search ", command=lambda: display_search(search_box.get()))
    search_button2.pack()

    quit_button = ttk.Button(search_page, text="Exit", command=search_page.destroy)
    quit_button.pack()

    search_page.geometry("500x500")
    search_page.mainloop()


def display_search(search_str):

    results = tk.Tk()
    results.wm_title("Search Results")

    search_results = api_requests.request_search_data(search_str)

    for stocks in search_results:
        symbol_button = ttk.Button(results, text=stocks,
                                   command=lambda stocks=stocks: info_page(stocks))
        symbol_button.pack()

    results.geometry('500x500')
    results.mainloop()


def info_page(stock):
    info = tk.Tk()
    info.wm_title(stock + " Info")

    label = ttk.Label(info, text=stock, font=LARGE_FONT)
    label.pack()
    stock_info = api_requests.request_full_stock_data(stock)

    label = tk.Label(info, text="", font=LARGE_FONT)
    label.pack()

    label = ttk.Label(info, text="Price: " + stock_info['05. price'], font=LARGE_FONT)
    label.pack()

    label = tk.Label(info, text="", font=LARGE_FONT)
    label.pack()

    label = ttk.Label(info, text="Open: " + stock_info['02. open'], font=LARGE_FONT)
    label.pack()

    label = tk.Label(info, text="", font=LARGE_FONT)
    label.pack()

    label = ttk.Label(info, text="High: " + stock_info['03. High'], font=LARGE_FONT)
    label.pack()

    label = tk.Label(info, text="", font=LARGE_FONT)
    label.pack()

    label = ttk.Label(info, text="Low: " + stock_info['04. low'], font=LARGE_FONT)
    label.pack()

    label = tk.Label(info, text="", font=LARGE_FONT)
    label.pack()

    label = ttk.Label(info, text="Previous Close: " + stock_info['08. previous close'], font=LARGE_FONT)
    label.pack()

    label = tk.Label(info, text="", font=LARGE_FONT)
    label.pack()

    label = ttk.Label(info, text="Change %: " + stock_info['10. change percent'], font=LARGE_FONT)
    label.pack()

    graph_button = ttk.Button(info, text='Graph', command=lambda: see_stock_graph(stock))
    graph_button.pack()

    global number_of_stocks
    number_of_stocks = tk.Entry(info, width=50)
    number_of_stocks.pack()
    number_of_stocks.insert(0, '# of stocks')

    global price_of_stock
    price_of_stock = tk.Entry(info, width=50)
    price_of_stock.pack()
    price_of_stock.insert(0, stock_info['05. price'])

    add_button = ttk.Button(info, text='Add', command=lambda: add_to_portfolio(stock, number_of_stocks.get(), price_of_stock.get()))
    add_button.pack()

    info.geometry('700x700')
    info.mainloop()


def add_to_portfolio(stock, units, price):
    price_of_stock.delete(0, 'end')
    number_of_stocks.delete(0, 'end')
    conn = sqlite3.connect("stock_manager.db")
    cur = conn.cursor()
    cur.execute('SELECT symbol from stocks')
    stock_list = cur.fetchall()
    exists = False

    for name in stock_list:
        if name[0] == stock:
            exists = True
            cur.execute('SELECT average_cost from stocks where symbol=?', (stock,))
            current = cur.fetchall()

            cur.execute('SELECT units from stocks where symbol=?', (stock,))
            num = cur.fetchall()

            new_units = int(units)+(num[0][0])
            new_price = (int(units)*float(price) + (current[0][0])*(num[0][0]))/new_units

            cur.execute('Update stocks set average_cost=?, units=? where symbol=?', (new_price, new_units, stock))
            conn.commit()
            conn.close()
            return

    if not exists:
        sql = '''INSERT INTO stocks(symbol, average_cost, units) 
        VALUES (?,?,?)'''
        info = (stock, price, units)
        cur.execute(sql, info)
        conn.commit()
        cur.close()


def see_stock_graph (stock):
    global url
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + stock + "&interval=5min&apikey=DBBCEP6J972FNU4I"


def connect_db():
    conn = sqlite3.connect("stock_manager.db")
    cur = conn.cursor()

    create_stock_table = """ CREATE TABLE IF NOT EXISTS stocks (
                                        symbol text PRIMARY KEY,
                                        average_cost int,
                                        units int
                                    );"""

    cur.execute(create_stock_table)


class StockManagerApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Stock Manager")
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        menubar = tk.Menu(container)
        tk.Tk.config(self, menu=menubar)

        filemenu = tk.Menu(menubar)

        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=quit)
        filemenu.add_command(label="Search", command=lambda: search())

        self.frames = {}

        for pages in (MainPage,):
            frame = pages(container, self)
            self.frames[pages] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)

        connect_db()

    def show_frame (self, page_name, arg=None):

        frame = self.frames[page_name]
        frame.tkraise()


class MainPage (tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Home Page", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button2 = ttk.Button(self, text="Show Graph", command=lambda: graph_page())
        button2.pack(anchor='ne')

        conn = sqlite3.connect("stock_manager.db")
        cur = conn.cursor()

        cur.execute('SELECT symbol from stocks')
        stock_list = cur.fetchall()

        see_stock_graph(stock_list[0][0])
        for item in stock_list:
            stock_button = ttk.Button(self, text=item[0], command=lambda: info_page(item[0]))
            stock_button.pack(anchor='w')
            cur.execute('SELECT average_cost from stocks where symbol=?', (item[0],))
            price = cur.fetchall()

            price_label = tk.Label(self, text='Average Price: '+str(price[0][0]), font=LARGE_FONT)
            price_label.pack(anchor='w')

            cur.execute('SELECT units from stocks where symbol=?', (item[0],))
            num = cur.fetchall()

            units_label = tk.Label(self, text='Units: '+str(num[0][0]), font=NORM_FONT)
            units_label.pack(anchor='w')

        restart_button = ttk.Button(self, text='Restart', command=lambda: restart())
        restart_button.pack(anchor='se')
        quit_button = ttk.Button(self, text='Quit', command=quit)
        quit_button.pack(anchor='se')


app = StockManagerApp()
app.geometry('1280x720')
app.mainloop()
