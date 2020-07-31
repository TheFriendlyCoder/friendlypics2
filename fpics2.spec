# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['src/friendlypics2/scripts/fpics2.py'],
             pathex=['src/friendlypics2'],
             binaries=[],
             datas=[('./src/friendlypics2/data/ui/*', 'friendlypics2/data/ui')],
             hiddenimports=['PySide2.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

# Windows executable
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='fpics2',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          # NOTE: setting console mode in Windows ensures the application waits until the user exits
          #       the app before returning control to the shell, ensuring that log output and status
          #       messages are properly reported
          # NOTE: setting console mode in MacOS causes the menu bar to misbehave, the native shortcut
          #       keys don't work, and the window opens behind the window that was used to launch the
          #       app. So we may want to use console mode for windows binaries and window mode for Mac
          console=False)

# Mac OS app
app = BUNDLE(exe,
             name='fpics2.app',
             icon=None,
             bundle_identifier=None)