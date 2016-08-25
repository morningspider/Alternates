import networkx as nx
import csv
from tkinter import *
from distutils.core import setup
import py2exe

def is_valid(ISBN):

    if len(ISBN) not in (10,13):
        return False

    if len(ISBN) == 10:
        s = 0
        if ISBN[-1] == 'X' or ISBN[-1] == 'x':
            isbn = int(ISBN[:-1])
            i = 2
            s += 10
        else:
            isbn = int(ISBN)
            i = 1

        while i < 11:
            digit = isbn%10
            s += i*digit
            isbn //= 10
            i+=1

        if s % 11 == 0:
            return True
        else:
            return False

    if len(ISBN) == 13:
        s = 0
        isbn = int(ISBN)

        for i in range(1,14):
            digit = isbn%10
            if i % 2 == 0:
                s+= digit*3
            else:
                s += digit
            isbn //= 10

        if s % 10 == 0:
            return True
        else:
            return False

class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self,master)
        self.master = master
        self.init_window()

    def init_window(self):
        #Initialize window with widgets

        #load alternates data
        f = open('alternates.csv')
        pairs = []
        reader = csv.reader(f)
        for row in reader:
            pairs.append(row)

        #create a graph from the list of edge pairs
        self.G1 = nx.Graph()
        self.G1.add_edges_from(pairs)

        #window title
        self.master.title("Alternate Checker")
        #pack whole window (not sure exactly what this does)
        self.pack(fill=BOTH, expand=1)

        #Create menu bar
        menu = Menu(self.master)
        self.master.config(menu=menu)

        #add File menu dropdown with Exit option
        file = Menu(menu)
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)

        #Add "ISBN" next to entry box
        isbn_label = Label(self, text="ISBN", width=25)
        isbn_label.grid(row=0)

        #Create entry bar and save as variable 'entrytext'
        self.entrytext = StringVar()
        e1 = Entry(self, textvariable=self.entrytext, width=13)
        e1.grid(row=0,column=1)

        #create button to get results
        b = Button(self, text="Get Alternates", command=self.getAlternates)
        b.grid(row=1)

        #initialize text box to print results into
        self.results = Text(self,height=10, width=25)

    def getAlternates(self):

        ISBN = self.entrytext.get()
        w = self.results
        w.delete(1.0, END)
        if is_valid(ISBN) == False:
            w.insert(1.0, "Invalid ISBN")
            return
        f = open('alternates.csv')
#        pairs = []
#        reader = csv.reader(f)
#        for row in reader:
#            pairs.append(row)
#        G1 = nx.Graph()
#        G1.add_edges_from(pairs)
        try:
            alternates = sorted(nx.node_connected_component(self.G1, ISBN))
            for alt in alternates:
                if alt == ISBN: continue
                w.insert(1.0, alt+"\n")
                w.grid(row=2)

        except KeyError:
            w.insert(1.0, "No Alternates")
            w.grid(row=2)

    def client_exit(self):
        exit()

def main():
    #initialize tkinter window
    root = Tk()
    root.geometry("300x225")
    app = Window(root)
    root.mainloop()

if __name__ == '__main__':
    main()




