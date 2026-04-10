import os
import re
import win32com.client
from tkinter import Tk, filedialog


def _sanitize_filename(name):
    """Replace characters illegal on Windows with underscores."""
    return re.sub(r'[/\\:*?"<>|]', '_', name.replace(" ", "_"))


def export_all_graph_traces(project_path=None, export_dir=None):
    # Prompt for project file if not provided
    if not project_path:
        root = Tk()
        root.withdraw()
        project_path = filedialog.askopenfilename(
            title="Select AWR Project File",
            filetypes=[("AWR Project Files", "*.emp *.vnet *.aws *.pjt")],
        )
        root.destroy()
        if not project_path:
            print("No project selected.")
            return

    # Prompt for export directory if not provided
    if not export_dir:
        root = Tk()
        root.withdraw()
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        root.destroy()
        if not export_dir:
            print("No export directory selected.")
            return

    # Initialize AWR Design Environment
    app = win32com.client.Dispatch("MWOApp.MWOfficeApp")
    app.Visible = True

    # Open the project
    project = app.OpenProject(project_path)
    print(f"Opened project: {project.Name}")

    exported = 0
    failed = 0
    total = 0
    used_filenames = set()

    try:
        # Loop through all graphs
        for graph in project.Graphs:
            graph_name = _sanitize_filename(graph.Name)
            print(f"Exporting traces for graph: {graph_name}")

            # Loop through all traces in the graph
            for trace in graph.Traces:
                total += 1
                trace_name = _sanitize_filename(trace.Name)
                base_name = f"{graph_name}__{trace_name}"

                # Handle duplicate filenames
                final_name = base_name
                counter = 2
                while final_name in used_filenames:
                    final_name = f"{base_name}_{counter}"
                    counter += 1
                used_filenames.add(final_name)

                export_file = os.path.join(export_dir, f"{final_name}.csv")

                try:
                    trace.ExportToFile(export_file, ",")  # comma-separated
                    print(f"Exported: {export_file}")
                    exported += 1
                except Exception as e:
                    print(f"Failed to export {graph_name} / {trace_name}: {e}")
                    failed += 1
    finally:
        # Close the project but do NOT quit AWR -- user may have it open for other work
        try:
            project.Close(False)  # False = do not save changes
        except Exception:
            pass

    print(f"Export complete: {exported} exported, {failed} failed out of {total} total traces.")


if __name__ == "__main__":
    export_all_graph_traces()
