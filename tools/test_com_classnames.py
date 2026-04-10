import win32com.client

possible_class_names = [
    "MWOApp.MWOfficeApp",              # Classic
    "MWOffice.Application",            # Reported in some AWR versions
    "MWOfficeApp.MWOfficeApp",         # Alternate
    "MicrowaveOffice.Application"      # Legacy
]

for cls_name in possible_class_names:
    try:
        print(f"Trying: {cls_name}")
        app = win32com.client.Dispatch(cls_name)
        print(f"✅ Connected using: {cls_name}")
        break
    except Exception as e:
        print(f"❌ Failed: {cls_name} — {e}")