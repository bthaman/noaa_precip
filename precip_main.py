"""
 written by bill thaman
 last update: 11/14/16

 application to ...
"""

import process_hourly
import precip_dialog
from send_sms import *
import Tkinter
import ttk


class App(precip_dialog.PrecipGUI):
    # inherits from PrecipGUI
    def __init__(self):
        precip_dialog.PrecipGUI.__init__(self)
        self.map_area = Tkinter.StringVar()
        self.map_area.trace('w', self.handle_event)
        ttk.Label(self, text='Area of Interest').grid(column=1, row=3, sticky='W')
        cmb_area = ttk.Combobox(self, textvariable=self.map_area, width=12)
        cmb_area.grid(column=2, row=3, sticky='E')
        cmb_area['values'] = ['texas', 'austin', 'bexar', 'dfw', 'harris']
        cmb_area.current(0)
        # put space around the widgets
        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    # override the tk window click event
    def okclick(self):
        # tk window's click event: get values from window
        duration_hrs = self.entered_duration.get()
        precip_date = self.selected_date.get()
        map_area = self.map_area.get()

        # close the window
        self.quit()

        pp = process_hourly.PrecipProcessor(precip_date)
        if duration_hrs != 'all':
            pp.process_points(duration_hrs, map_area, create_raster=False)
        else:
            process_hourly.PrecipProcessor.process_all_durations = True
            for d in self.get_durations():
                pp.process_points(d, map_area=map_area, export_maps=True, show_maps=False, create_raster=False)
            if pp.max_return_period >= 100:
                send_text('\nDate: ' + str(pp.precip_date) + '\n' + 'Max return period: ' +
                          str(pp.max_return_period) + '\n' + 'County: ' + pp.max_return_period_county)

    # override super class event
    def handle_event(self, *args):
        x = self.selected_date.get()
        y = self.entered_duration.get()
        z = self.map_area.get()
        if x and y and z:
            self.btn_ok.configure(state='normal')
        else:
            self.btn_ok.configure(state='disabled')


if __name__ == "__main__":
    app = App()
    app.show_window()
