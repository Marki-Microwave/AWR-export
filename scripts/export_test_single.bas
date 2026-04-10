' Diagnostic: just list graph names
Sub Main
    Dim i As Integer
    Dim g As Graph

    Debug.Print "Graph count: " & Project.Graphs.Count

    For i = 1 To Project.Graphs.Count
        Set g = Project.Graphs(i)
        Debug.Print "  " & i & ": " & g.Name
    Next i

    Debug.Print "Done."
End Sub
