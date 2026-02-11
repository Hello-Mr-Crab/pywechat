from setuptools import setup,find_packages
setup(name='pywechat127',
version='1.9.9',
author='Hello-Mr-Crab',
author_email='3083256475@qq.com',
classifiers=[
"Operating System :: Microsoft :: Windows",
],
platforms=["Windows"],
description=f'A Powerful Windows-PC-Wechat automation Tool',
long_description=open('README.md','r',encoding='utf-8').read(),
long_description_content_type='text/markdown',  
url='https://github.com/Hello-Mr-Crab/pywechat',
packages=find_packages(),
license='LGPL',
keywords=['rpa','windows','wechat','automation'],
install_requires=[
'emoji>=2.14.1','PyAutoGUI>=0.9.54','pycaw>=20240210','pywin32>=308','pywin32-ctypes>=0.2.2','pywinauto>=0.6.8','psutil>=5.9.6','pillow>=10.4.0']
)
'''
Author:Hello-Mr-Crab
Contributor:Viper,Chanpoe,mrhan1993,nmhjklnm,clen1,guanjt3
'''
