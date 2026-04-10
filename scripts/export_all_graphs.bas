' Export All Graph Trace Data
' Activates each graph before export (mimics manual workflow).

' $MENU=Scripts
Sub Main
    Dim g As Graph
    Dim exportDir As String
    Dim filepath As String
    Dim graphName As String
    Dim exported As Integer
    Dim total As Integer

    exportDir = "C:\Users\severin.pindell\PycharmProjects\AWR\output\"

    exported = 0
    total = 0

    For Each g In Project.Graphs
        total = total + 1
        graphName = g.Name
        graphName = Replace(graphName, "/", "_")
        graphName = Replace(graphName, "\", "_")
        graphName = Replace(graphName, ":", "_")
        graphName = Replace(graphName, "*", "_")
        graphName = Replace(graphName, "?", "_")
        graphName = Replace(graphName, """", "_")
        graphName = Replace(graphName, "<", "_")
        graphName = Replace(graphName, ">", "_")
        graphName = Replace(graphName, "|", "_")
        graphName = Replace(graphName, " ", "_")

        filepath = exportDir & graphName & ".txt"

        On Error Resume Next
        Err.Clear

        ' Activate the graph first — mimics selecting it in the UI
        g.Activate

        If Err.Number <> 0 Then
            Debug.Print "SKIP (activate failed): " & g.Name & " - " & Err.Description
            Err.Clear
        Else
            g.ExportTraceData filepath

            If Err.Number = 0 Then
                exported = exported + 1
                Debug.Print "OK: " & g.Name
            Else
                Debug.Print "SKIP (export failed): " & g.Name & " - " & Err.Description
                Err.Clear
            End If
        End If
    Next g

    On Error GoTo 0

    Debug.Print "Done: " & exported & " of " & total & " graphs exported."
    Debug.Print "Output: " & exportDir
End Sub
