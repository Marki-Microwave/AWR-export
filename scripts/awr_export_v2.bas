' Export All Graph Trace Data
' Only exports graphs that have an open window.
' Graphs without windows are skipped to avoid crashes.

Sub Main
    Dim g As Graph
    Dim exportDir As String
    Dim filepath As String
    Dim graphName As String
    Dim exported As Integer
    Dim skipped As Integer
    Dim total As Integer
    Dim hasWindow As Boolean

    exportDir = "C:\Users\severin.pindell\PycharmProjects\AWR\output\"

    exported = 0
    skipped = 0
    total = 0

    On Error Resume Next

    For Each g In Project.Graphs
        total = total + 1

        ' Check if graph has an open window
        Err.Clear
        hasWindow = (g.Windows.Count > 0)

        If Err.Number <> 0 Or Not hasWindow Then
            skipped = skipped + 1
            Debug.Print "SKIP (no window): " & g.Name
            Err.Clear
        Else
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

            Err.Clear
            g.ExportTraceData filepath

            If Err.Number = 0 Then
                exported = exported + 1
                Debug.Print "OK: " & g.Name
            Else
                skipped = skipped + 1
                Debug.Print "SKIP (export failed): " & g.Name & " - " & Err.Description
                Err.Clear
            End If
        End If
    Next g

    On Error GoTo 0

    Debug.Print "Done: " & exported & " exported, " & skipped & " skipped, " & total & " total."
    Debug.Print "Output: " & exportDir
End Sub
