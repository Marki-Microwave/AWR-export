from win32com.client import GetActiveObject

try:
    app = GetActiveObject("MWOApp.MWOfficeApp")
    print("✅ Successfully attached to running AWR instance!")
except Exception as e:
    print("❌ GetActiveObject failed:", e)
