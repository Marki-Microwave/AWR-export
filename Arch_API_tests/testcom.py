import win32com.client
import platform

from win32com.client import gencache

try:
    # Force Python to generate wrapper files
    app = gencache.EnsureDispatch("MWOApp.MWOfficeApp")
    print("✅ COM dispatch successful.")
except Exception as e:
    print("❌ EnsureDispatch failed:", e)


def list_all_com_classes():
    print("Searching for AWR-related COM classes...\n")
    com_classes = win32com.client.gencache.GetGeneratedInfos()
    for cls in com_classes:
        print(cls)

if __name__ == "__main__":
    list_all_com_classes()

    print(platform.architecture())