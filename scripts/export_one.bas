' Export just graph 1 — no Activate, no guard
Sub Main
    Dim g As Graph
    Set g = Project.Graphs(1)
    Debug.Print "Exporting: " & g.Name

    On Error Resume Next
    g.ExportTraceData "C:\Users\severin.pindell\PycharmProjects\AWR\output\graph1_test.txt"
    If Err.Number = 0 Then
        Debug.Print "OK"
    Else
        Debug.Print "ERROR: " & Err.Description
    End If
    On Error GoTo 0
End Sub
