' Test: export just the first graph
' $MENU=Scripts
Sub Main
    Dim g As Graph
    Set g = Project.Graphs(1)

    Debug.Print "Activating: " & g.Name
    g.Activate

    Debug.Print "Exporting..."
    g.ExportTraceData "C:\Users\severin.pindell\PycharmProjects\AWR\output\single_test.txt"

    Debug.Print "Done."
End Sub
