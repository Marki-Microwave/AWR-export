import pandas as pd
import tkinter as tk
from tkinter import filedialog

class APFileParser:
    def __init__(self, file_path: str = None):
        """
        Initialize and parse the AP-formatted file. If no path is provided, opens a file dialog.
        """
        self.file_path = file_path or self._get_file_via_dialog()
        self.df = None
        self.column_mapping = {}  # Maps cleaned name -> full original name
        self._parse()

    def _get_file_via_dialog(self) -> str:
        """
        Opens a file dialog for the user to select a file.
        """
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        file_path = filedialog.askopenfilename(
            title="Select MWO Graph Data File",
            filetypes=[("MWO  Data File", "*.txt"), ("All Files", "*.*")]
        )
        root.destroy()
        if not file_path:
            raise FileNotFoundError("No file selected.")
        return file_path

    def _parse(self):
        """
        Internal method to parse the file into a pandas DataFrame.
        """
        raw_df = pd.read_csv(self.file_path, sep='\t')

        cleaned_columns = []
        seen_counts = {}  # tracks how many times each cleaned name has appeared
        for col in raw_df.columns:
            if ':' in col:
                base_name, metadata = col.split(':', 1)
                cleaned_name = base_name.strip()
            else:
                cleaned_name = col.strip()

            if cleaned_name in seen_counts:
                seen_counts[cleaned_name] += 1
                unique_name = f"{cleaned_name}_{seen_counts[cleaned_name]}"
            else:
                seen_counts[cleaned_name] = 1
                unique_name = cleaned_name

            self.column_mapping[unique_name] = col
            cleaned_columns.append(unique_name)

        raw_df.columns = cleaned_columns
        self.df = raw_df

    def to_dict(self) -> dict:
        """
        Returns the data as a dictionary {column_name: ndarray of values}
        """
        return {col: self.df[col].values for col in self.df.columns}

    def get_dataframe(self) -> pd.DataFrame:
        """
        Returns a copy of the parsed pandas DataFrame.
        """
        return self.df.copy()

    def get_original_column_name(self, cleaned_name: str) -> str:
        """
        Returns the full original column name for a given cleaned column name.
        """
        return self.column_mapping.get(cleaned_name)
