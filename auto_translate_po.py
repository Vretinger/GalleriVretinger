import polib
from deep_translator import GoogleTranslator

po_file_path = "locale/sv/LC_MESSAGES/django.po"
po = polib.pofile(po_file_path)

translator = GoogleTranslator(source='en', target='sv')

for entry in po:
    # Ensure all string fields are not None
    if entry.msgstr is None:
        entry.msgstr = ""
    if entry.msgid is None:
        entry.msgid = ""
    if entry.msgctxt is None:
        entry.msgctxt = ""

    # Translate if msgstr is empty
    if not entry.msgstr and entry.msgid:
        try:
            translated = translator.translate(entry.msgid)
            if translated is None:
                translated = ""
            entry.msgstr = translated
            print(f"Translated: {entry.msgid} -> {entry.msgstr}")
        except Exception as e:
            print(f"Failed to translate '{entry.msgid}': {e}")

po.save(po_file_path)
print("All translations updated! Compile with `django-admin compilemessages`")
