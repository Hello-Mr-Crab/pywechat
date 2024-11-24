from setuptools import setup,find_packages
setup(name='pywechat127',
version='2.0',
author='Hello-Mr-Crab',
author_email='3083256475@qq.com',
description=f'A Powerful Windows-PC-Wechat automation Tool',
long_description=open('README.md','r',encoding='utf-8').read(),
long_description_content_type='text/markdown',  
url='https://github.com/Hello-Mr-Crab/pywechat',
packages=find_packages(),
license='Apache-2.0',
keywords=['windows','wechat','automation'],
install_requires=['psutil',
'PyAutoGUI>=0.9.54','pycaw>=20240210','pywin32>=308','pywin32-ctypes>=0.2.2','pywinauto>=0.6.8','psutil>=5.9.6']
)
