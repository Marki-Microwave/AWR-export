import os
import win32com.client
from tkinter import Tk, filedialog

def export_all_graph_traces(project_path=None, export_dir=None):
    # Prompt for project file if not provided
    if not project_path:
        Tk().withdraw()
        project_path = filedialog.askopenfilename(title="Select AWR Project File",
                                                  filetypes=[("AWR Project Files", "*.emp *.vnet *.aws *.pjt")])
        if not project_path:
            print("No project selected.")
            return

    # Prompt for export directory if not provided
    if not export_dir:
        Tk().withdraw()
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            print("No export directory selected.")
            return

    # Initialize AWR Design Environment
    app = win32com.client.Dispatch("MWOApp.MWOfficeApp")
    app.Visible = True

    # Open the project
    project = app.OpenProject(project_path)
    print(f"Opened project: {project.Name}")

    # Loop through all graphs
    for graph in project.Graphs:
        graph_name = graph.Name.replace(" ", "_")
        print(f"Exporting traces for graph: {graph_name}")

        # Loop through all traces in the graph
        for trace in graph.Traces:
            trace_name = trace.Name.replace(" ", "_")
            export_file = os.path.join(export_dir, f"{graph_name}__{trace_name}.csv")

            try:
                trace.ExportToFile(export_file, ",")  # comma-separated
                print(f"Exported: {export_file}")
            except Exception as e:
                print(f"Failed to export {graph_name} / {trace_name}: {e}")

    print("All graph traces exported.")

if __name__ == "__main__":
    export_all_graph_traces()
