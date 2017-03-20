import Tkinter
import ttk
import file_mgmt as fm


class DDFplotGUI(ttk.LabelFrame):
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.wm_title('DDF Dates')
        ttk.LabelFrame.__init__(self, self.root, text="DDF Dates")
        self.padding = '6, 6, 12, 12'
        self.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.selected_date = Tkinter.StringVar()
        self.selected_date.trace('w', self.handle_event)

        self.btn_ok = ttk.Button(self, text='OK', width=7, command=self.okclick)
        self.dropdown_list = fm.csv_precip_list()

        ttk.Label(self, text='Precip Date').grid(column=1, row=2, sticky='W')
        cmb_date = ttk.Combobox(self, textvariable=self.selected_date, width=12)

        cmb_date.grid(column=2, row=2, sticky='E')
        self.btn_ok.grid(row=4, columnspan=3)
        self.btn_ok.configure(state='disabled')

        cmb_date['values'] = self.dropdown_list
        if len(self.dropdown_list) > 0:
            cmb_date.current(0)

        # put space around the widgets
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def okclick(self):
        # click event for btn_ok. this should be overridden by any superclass
        print('override me!')

    def handle_event(self, *args):
        x = self.selected_date.get()

        if x:
            self.btn_ok.configure(state='normal')
        else:
            self.btn_ok.configure(state='disabled')

    def set_dropdown(self, the_list):
        self.dropdown_list = the_list

    def show_window(self):
        self.root.mainloop()

    def quit(self):
        try:
            self.root.destroy()
        except Exception as e:
            print e


if __name__ == "__main__":
    gui = DDFplotGUI()
    gui.show_window()




