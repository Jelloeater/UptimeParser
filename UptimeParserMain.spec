# -*- mode: python -*-

block_cipher = None


a = Analysis(['UptimeParserApp\\UptimeParserMain.py'],
             pathex=['Y:\\CodingWorkspace\\UptimeParser'],
             #Change this path to wherever your root project dir is

             binaries=[],
             datas=[],
             hiddenimports=['pysnmp.smi.exval','pysnmp.cache'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

x = Tree('C:/Python37-32/Lib/site-packages/pysnmp/smi/mibs',prefix='pysnmp/smi/mibs',excludes='.py')
# Change this to the location of your MIBs package on your python install that is in you PATH

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          x,
          [],
          name='UptimeParserMain',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
