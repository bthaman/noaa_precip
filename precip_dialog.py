import Tkinter
import ttk
import ttkcalendar
import datetime

import tkSimpleDialog


class CalendarDialog(tkSimpleDialog.Dialog):
    """Dialog box that displays a calendar and returns the selected date"""
    def body(self, master):
        self.calendar = ttkcalendar.Calendar(master)
        self.calendar.pack()

    def apply(self):
        self.result = self.calendar.selection


class PrecipGUI(ttk.LabelFrame):
    def __init__(self):
        self.root = Tkinter.Tk()
        self.root.wm_title('Precipitation Analysis')
        ttk.LabelFrame.__init__(self, self.root, text="Precip Analysis")
        self.padding = '6, 6, 12, 12'
        self.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        def getdate():
            cd = CalendarDialog(self)
            result = cd.result
            self.selected_date.set(result.strftime("%m/%d/%Y"))

        self.selected_date = Tkinter.StringVar()
        self.selected_date.trace('w', self.handle_event)
        self.entered_duration = Tkinter.StringVar()
        self.entered_duration.trace('w', self.handle_event)
        self.lst_duration = ['1', '3', '6', '12', '24']

        self.btn_ok = ttk.Button(self, text='OK', width=7, command=self.okclick)

        txt_date = ttk.Entry(self, textvariable=self.selected_date, width=15)
        btn_choose_date = ttk.Button(self, text="Choose a date", command=getdate)

        ttk.Label(self, text='Duration (hrs)').grid(column=1, row=2, sticky='W')
        cmb_duration = ttk.Combobox(self, textvariable=self.entered_duration, width=12)

        txt_date.grid(column=2, row=1, sticky='E')
        btn_choose_date.grid(column=1, row=1, sticky='W')
        cmb_duration.grid(column=2, row=2, sticky='E')
        self.btn_ok.grid(row=4, columnspan=3)
        self.btn_ok.configure(state='disabled')

        cmb_duration['values'] = self.lst_duration + ['all']

        # put space around the widgets
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def okclick(self):
        # click event for btn_ok. this should be overridden by any superclass
        try:
            if self.entered_duration.get() not in ('3', '6', '12', '24'):
                raise ValueError
        except ValueError:
            raise ValueError('Duration must be 3, 6, 12, or 24')
        try:
            datetime.datetime.strptime(self.selected_date.get(), '%m/%d/%Y')
        except ValueError:
            raise ValueError('Date format is mm/dd/yyyy')
        print(self.selected_date.get(), self.entered_duration.get())

    def handle_event(self, *args):
        x = self.selected_date.get()
        y = self.entered_duration.get()

        if x and y:
            self.btn_ok.configure(state='normal')
        else:
            self.btn_ok.configure(state='disabled')

    def get_durations(self):
        return self.lst_duration

    def show_window(self):
        self.root.mainloop()

    def quit(self):
        self.root.destroy()


if __name__ == "__main__":
    gui = PrecipGUI()
    gui.show_window()




