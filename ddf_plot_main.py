"""
 written by bill thaman
 last update: 11/14/16

 application to ...
"""

import ddf_plot_dialog
import ddf_plotting


class App(ddf_plot_dialog.DDFplotGUI):
    # inherits from DDFplotGUI
    def __init__(self):
        ddf_plot_dialog.DDFplotGUI.__init__(self)

    # override the tk window click event
    def okclick(self):
        # tk window's click event: get values from window
        precip_date = self.selected_date.get()
        self.quit()

        # print("test")
        ddfp = ddf_plotting.DDFplotting(precip_date)
        ddfp.plot_precip_date_ddf()


if __name__ == "__main__":
    app = App()
    app.show_window()
