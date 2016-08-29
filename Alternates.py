import networkx as nx
import csv
from tkinter import *
import pymssql
import webbrowser
import _mssql

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
def ISBN13_to_10(ISBN):
    truncated = int(ISBN[3:-1])
    s = 0
    for i in range(2,11):
        digit = truncated%10
        s += i*digit
        truncated //= 10
    check = (-s) % 11
    if check == 10:
        check = 'X'
    output = "{}{}".format(ISBN[3:-1], check)
    return output
class Window(Frame):

    def __init__(self, master=None):
        Frame.__init__(self,master)
        self.master = master
        self.init_window()

    def init_window(self):
        #Initialize window with widgets

        #Connect to database
        conn = pymssql.connect(
            host=r'mssql3.gear.host',
            user=r'superioreporting',
            password='7jgX3NVKBCdHL8DYfD9!',
            database='superiortext')
        self.cursor = conn.cursor()

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

        #Create entry bar and set input to variable 'entrytext'
        self.entrytext = StringVar()
        e1 = Entry(self, textvariable=self.entrytext, width=13)
        e1.grid(row=0,column=0, sticky=W)

        #create button to get results
        b = Button(self, text="Get Alternates", command=self.getAlternates)
        b.grid(row=1, sticky=W)

        isbn_header = Label(self, text='ISBN', font="Helvetica 10 bold")
        isbn_header.grid(row=2, column=0, sticky=W)

        title_header = Label(self, text='Title', font="Helvetica 10 bold")
        title_header.grid(row=2, column=1, sticky=W)

        copyright_header = Label(self, text='©', font="Helvetica 10 bold")
        copyright_header.grid(row=2, column=2, sticky=W)

        publisher_header = Label(self, text='Publisher', font="Helvetica 10 bold")
        publisher_header.grid(row=2, column=3, sticky=W)


        #current ISBN labels
        self.CurrentBookISBN = Label(self, text='', font="Helvetica 10")
        self.CurrentBookISBN.grid(row=3, column=0, sticky=W)

        self.CurrentBookTitle = Label(self, text="", font="Helvetica 10")
        self.CurrentBookTitle.grid(row=3, column=1, sticky=W)

        self.CurrentBookCopyright = Label(self, text="", font="Helvetica 10")
        self.CurrentBookCopyright.grid(row=3, column=2, sticky=W)

        self.CurrentBookPublisher = Label(self, text="", font="Helvetica 10")
        self.CurrentBookPublisher.grid(row=3, column=3, sticky=W)

        #initialize text box to print results into
        self.results = Text(self,height=10, width=14, font="Helvetica 10")
        self.results.grid(row=4, sticky=W)

        #initialize text boxes to print descriptions
        self.titles = Text(self,height=10, width=25, wrap=NONE, font="Helvetica 10")
        self.titles.grid(row=4, column=1, sticky=W)

        self.copyrights = Text(self,height=10, width=4, wrap=NONE, font="Helvetica 10")
        self.copyrights.grid(row=4, column=2, sticky=W)

        self.publishers = Text(self,height=10, width=25, wrap=NONE, font="Helvetica 10")
        self.publishers.grid(row=4, column=3, sticky=W)

    def open_links(self, ISBN_list):
        for ISBN in ISBN_list:
            url = 'https://www.amazon.com/exec/obidos/ASIN/{}/'.format(ISBN)
            webbrowser.open_new_tab(url)

    def getAlternates(self):
        #retrieve given ISBN from entry widget
        ISBN = self.entrytext.get()

        #assign results text box to variable and clear it
        w = self.results
        w.delete(1.0, END)

        self.CurrentBookISBN.config(text='')
        self.CurrentBookTitle.config(text='')
        self.CurrentBookCopyright.config(text='')
        self.CurrentBookPublisher.config(text='')

        #clear the description text boxes
        self.titles.delete(1.0, END)
        self.copyrights.delete(1.0, END)
        self.publishers.delete(1.0, END)

        #check ISBN is valid
        if is_valid(ISBN) == False:
            w.insert(1.0, "Invalid ISBN")
            return

        #convert to ISBN-10
        if len(ISBN) == 13:
            ISBN = ISBN13_to_10(ISBN)

        #pull book data for given ISBN
        try:
            self.cursor.execute("SELECT Title, CopyrightYear, Publisher FROM Book WHERE ISBN = '{}'".format(ISBN))
            (Title, CopyrightYear, Publisher) = self.cursor.fetchone()
        except TypeError:
            Title, CopyrightYear, Publisher = "Not in Database", "", ""

        #create Labels for given ISBN data
        self.CurrentBookISBN.config(text=ISBN,)
        self.CurrentBookTitle.config(text=Title)
        self.CurrentBookCopyright.config(text=CopyrightYear)
        self.CurrentBookPublisher.config(text=Publisher)

        box_size = 25
        try:
            #pull all connected components from graph
            alternates = sorted(nx.node_connected_component(self.G1, ISBN))
            alternates.remove(ISBN)

            for alt in alternates:
                #query database
                try:
                    self.cursor.execute("SELECT Title, CopyrightYear, Publisher FROM Book WHERE ISBN = '{}'".format(alt))
                    (Title, CopyrightYear, Publisher) = self.cursor.fetchone()

                #if ISBN is not in database then execute() will return None Type
                except TypeError:
                    Title, CopyrightYear, Publisher = "Not in Database", "", ""

                #populate description textbox
                self.titles.insert(1.0,"{}\n".format(Title))
                self.copyrights.insert(1.0,"{}\n".format(CopyrightYear))
                self.publishers.insert(1.0, "{}\n".format(Publisher))

                #check to see if we need to resize the textbox
                if len(Title) > box_size:
                    box_size = len(Title)

                #populate ISBN text box
                w.insert(1.0, "{} \n".format(alt))

            #resize description text box
            self.titles.config(width=box_size)

            # add button
            button = Button(self, text='Open ISBNs in Amazon', command=lambda ISBNs=alternates: self.open_links(ISBNs))
            button.grid(row=5, column=0)

        #connected components queries a dict; will throw a KeyError if ISBN is not in the list
        except KeyError:
            w.insert(1.0, "No Alternates")
            # add button
            button = Button(self, text='Open ISBNs in Amazon')
            button.grid(row=5, column=0)

    def client_exit(self):
        exit()


def main():
    #initialize tkinter window
    root = Tk()
    root.geometry("800x600")
    app = Window(root)
    root.mainloop()

if __name__ == '__main__':
    main()




