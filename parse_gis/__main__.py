from pathlib import Path
from tkinter import Tk, Toplevel, filedialog, ttk, StringVar, IntVar
from geopandas import GeoDataFrame, read_file  # type: ignore[import-untyped]
import pandas as pd

from parse_gis.script import get_score

def extract_number_attributes(df: GeoDataFrame):
    # Implement your data extraction logic here
    # This is a placeholder, replace it with your actual code
    data = [key for key in df.select_dtypes(include=["number"])]
    return data


def get_min_max(df: GeoDataFrame, col: str):
    return df[col].min(), df[col].max()


class GUI:
    def __init__(self, root: Tk, *args):
        self.root = root
        self.show_welcome()
        self.root.title("Data Extraction and Processing")

    def proceess_attributes(self):
        top = Toplevel(self.root, name="attributes")
        self.attributes = extract_number_attributes(self.df)
        self.attribute_vars: list[StringVar] = [StringVar() for _ in self.attributes]
        self.attribute_intervals: list[IntVar] = [
            IntVar(value=10) for _ in self.attributes
        ]
        self.chk_entries: list[ttk.Checkbutton] = []
        self.set_checkboxes = []
        self.interval_entries: list[ttk.Entry] = []
        self.show_buttons = []

        self.labels = ["Attribute", "Show Values", "Score Range", "Min/Max"]
        self.menu = []
        for i, label in enumerate(self.labels):
            _label = ttk.Label(top, text=label, underline=1)
            _label.grid(row=0, column=i)
            self.menu.append(_label)

        self.min_max = []
        for i, attr in enumerate(self.attributes):
            row = i + 1
            chk = ttk.Checkbutton(
                top,
                text=attr,
                variable=self.attribute_vars[i],
                onvalue=True,
                offvalue=False,
                command=self.mark_checkbox(i),
            )
            chk.grid(row=row, column=0, sticky="w")
            self.set_checkboxes.append(False)
            self.chk_entries.append(chk)

            button = ttk.Button(top, text="Show", command=self.show_values(attr))
            button.grid(row=row, column=1)
            self.show_buttons.append(button)

            interval_entry = ttk.Entry(top, textvariable=self.attribute_intervals[i])
            interval_entry.grid(row=row, column=2)
            self.interval_entries.append(interval_entry)


            min_val, max_val = get_min_max(self.df, attr)
            label = ttk.Label(top, text=f"Min: {min_val}, Max: {max_val}")
            label.grid(row=row, column=3)
            self.min_max.append(label)

        def submit():
            self.process_data()

        submit_button = ttk.Button(top, text="Submit & Save", command=submit)
        submit_button.grid(row=len(self.attributes) + 1, column=0, columnspan=5)

    def get_file(self):
        self.file_path = Path(filedialog.askopenfilename())
        self.df: GeoDataFrame = read_file(self.file_path)
        self.proceess_attributes()

    def show_welcome(self):
        # Show welcome message on a tkinter window
        # top = Toplevel(self.root, name="welcome")
        # top.geometry("400x400")
        ttk.Label(
            self.root, text="Welcome to the Data Extraction and Processing Tool"
        ).pack()
        ttk.Label(self.root, text="Pick up a file to start processing").pack()

        def _get_file():
            # top.destroy()
            self.get_file()

        ttk.Button(self.root, text="Browse...", command=_get_file).pack()
        # top.wait_window()

    def mark_checkbox(self, i):
        def _set_checkboxes():
            self.set_checkboxes[i] = not self.set_checkboxes[i]

        return _set_checkboxes

    def show_values(self, col: str):
        # Show values on a tkinter windows from the df
        def _show_values():
            top = Toplevel(self.root, name=f"values in {col}")
            top.geometry("200x500")
            self.df[col].sort_values()
            for value in self.df[col].sort_values():
                ttk.Label(top, text=value).pack()

        return _show_values

    def process_data(self):
        for i, check_att in enumerate(self.chk_entries):
            if not self.set_checkboxes[i]:
                continue
            col = check_att.cget("text")
            interval = self.attribute_intervals[i].get()
            self.set_scores_for_col(col, interval)
        self.save_results()

    def save_results(self):
        self.root.withdraw()
        known_drivers = [
            ("all files", "*.*"),
            ("ESRI Shapefile", "*.shp"),
            ("GeoJSON", "*.geojson"),
            ("CSV", "*.csv"),
            ("GPKG", "*.gpkg"),
            ("KML", "*.kml"),
            ("SQLite", "*.sqlite"),
        ]
        save_path = Path(
            filedialog.asksaveasfilename(
                defaultextension=".shp", filetypes=known_drivers
            )
        )
        # Implement your result saving logic here
        # This is a placeholder, replace it with your actual code
        if not save_path.parent.exists():
            save_path.parent.mkdir(parents=True)
        try:
            if save_path.suffix.lower() in ".csv":
                self.df.drop(columns=["geometry"])
                self.df.to_csv(save_path)
            else:
                self.df.to_file(save_path)
            top = Toplevel(self.root, name="filesaved")
            top.geometry("500x100")
            ttk.Label(top, text=f"File saved to {save_path}").pack()
            ttk.Button(top, text="Close", command=top.destroy).pack()
            self.root.wait_window(top)
        except Exception as e:
            top = Toplevel(self.root, name="errorfilenotsaved")
            top.geometry("200x200")
            ttk.Label(top, text="Error saving results").pack()
            ttk.Label(top, text=str(e)).pack()
            ttk.Button(top, text="Close", command=top.destroy).pack()
            self.root.wait_window(top)
        self.root.destroy()

    def set_scores_for_col(self, col: str, range: int):
        self.df[col].apply(pd.to_numeric)
        min_val = self.df[col].min()
        max_val = self.df[col].max()
        score_calculator = get_score(
            min_max_values=(min_val, max_val), bounds=(1, range)
        )
        res_col = col + "_score"
        self.df[res_col] = self.df[col].apply(score_calculator)
        self.df[res_col] = self.df[res_col].astype("Int64")


def main():
    root = Tk()
    GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
