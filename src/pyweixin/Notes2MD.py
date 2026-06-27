'''
Notes2MD
===========

打开一个笔记时，微信会在.../business/favorite/temp内缓存当前笔记内的所有内容(除位置卡片外)
文件,图片,视频都是直接保存到这个文件夹里,笔记内容保存在一个htm内,笔记内粘贴的图片,视频,录音
位置卡片,文件等在htm里都在一个具有date_type属性的<object></object>标签内占位。
该模块需要做的就是按照这个html的内容和文件映射关系将其转变成可读,语法无误的MarkDown:

    - `export_weixin_note`:将微信缓存文件夹内的所有内容转为MarkDown
    - `remove_thumbs`:微信笔记内只要是图片,视频,Gif都会产生缩略图,该函数用于准确无误的去掉缩略图
'''

import os
import stat
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md

def remove_thumbs(folder_path)->None:
    '''
    分组比较的方式来删除所有缩略图
    Args:
        folder_path:存放微信收藏笔记缓存的文件夹
    '''
    #缩略图中没有任何表识,好在原图和缩略图的数字是挨着成对出现,所以只能采取这种方式
    #按文件名排序（让同组的图挨在一起）
    #两两一组，比较大小，保留大的（原图），删小的（缩略图）
    #落单的是视频或者Gif缩略图直接删除
    images=[]
    for name in os.listdir(folder_path):
        if name.lower().endswith('.jpg'):
            path=os.path.join(folder_path, name)
            size=os.path.getsize(path)
            images.append((size, path, name))
    if not images:
        return
    i=0
    #按文件名排序（让同组的图尽量挨在一起）
    images.sort(key=lambda x: x[2]) #按文件名排序
    n=len(images)
    while i<n:
        #两两一组处理
        if i+1<n:
            #有下一张，组成一对
            size1,path1,name1=images[i]
            size2,path2,name2=images[i+1]

            #比较大小，保留大的
            if size1>size2:
                #第1张是大图，保留，删第2张
                os.chmod(path2, stat.S_IWRITE)
                os.remove(path2)
                i+=2#跳到下一组
            else:
                #第2张是大图，保留，删第1张
                os.chmod(path1, stat.S_IWRITE)
                os.remove(path1)
                i+=2#跳到下一组
        else:
            #落单的，直接删除，视频或者Gif缩略图
            size1,path1,name1=images[i]
            os.chmod(path, stat.S_IWRITE)
            os.remove(path)
            i+=1

def clean_weixin_markdown(text:str)->str:
    '''正则规范微信笔记内容为markdown'''
    out_lines=[]
    in_code_block=False
    text=text.replace(r'\_', '_')
    lines=text.splitlines()
    for line in lines:
        stripped=line.strip()
        if stripped.startswith("```"):
            in_code_block=not in_code_block
            out_lines.append(line)
            continue
        if in_code_block:
            out_lines.append(line)
            continue
        line=re.sub(r"[\t]{2,}", " ", line)
        if stripped==""and out_lines and out_lines[-1].strip()=="":
            continue
        out_lines.append(line)
    result="\n".join(out_lines)
    result=re.sub(r"\n{3,}","\n\n",result)
    return result.strip()

def resolve_object_resource(obj,resource_dir:str,processed_files:set)->str:
    '''识别微信收藏缓存内的htm内图片视频文件三种资源的映射关系然后返回合适的MarkDown语句
    Args:
        obj:html的obj标签,Beautifulsoup查找到的对象
        processed_files:已经处理过的文件集合
    Returns:

        ```
        图片:![image](image.png)
        视频:<video src=".mp4" controls width="600"></video>
        文件:[测试.txt](测试.txt)
        ```
    '''
    #如果data-type是8但是文件后缀还是属于图片那么还应该用图片的markdown语法![](),而不是文件链接[]()
    IMAGE_EXTENSIONS=(
    '.jpg', '.jpeg', '.png',
    '.svg', '.webp', '.bmp', '.ico',
    '.apng', '.avif', '.tiff', '.tif'
    )
    data_type=obj.get("data-type", "")
    if not data_type:#纯文本
        return ""
    files=[
        f for f in os.listdir(resource_dir)
        if f not in processed_files
    ]
    matched_file=None
    #语音
    # .speex_temp是微信AES和xor加密后的语音文件,不逆向无法解密转换为mp3，这里不逆向只保留源文件)
    #但比较sb的是这个文件后缀带下划线_ ,markdownify会自动转义成\_，导致路径被自动切分
    # D:\test\语音.speex_temp会自动变成.D:\test\语音.speex\_temp,但还不能replace('_','其他')，不然文件后缀变了不可用
    if data_type=='3':
        for f in files:
            if f.lower().endswith(".speex_temp"):
                matched_file=f
                break
        processed_files.add(matched_file)
        #语音不做任何处理，就当做一个链接插入吧
        return f"\n[语音]({matched_file})\n"
    else:
        #图片，无论什么格式图片，最终在微信缓存中显示的都是jpg
        if data_type=="2":
            for f in files:
                if f.lower().endswith(('.jpg','.jpeg')):
                    matched_file=f
                    break
        #视频
        elif data_type=="4":
            for f in files:
                if f.lower().endswith('.mp4'):
                    matched_file=f
                    break
        #其他文件
        elif data_type=="8":
            for f in files:
                if not f.lower().endswith(('.jpg','.jpeg','.htm','.speex_temp')):
                    matched_file=f
                    break
        # 链接卡片（无文件）
        elif data_type=="6":
            return ""

        if not matched_file:
            return f"[⚠️ 资源未找到 (type={data_type})]\n"
        #所有需要按照文件路径插入链接的对象,图片,视频,文件都要规范路径把_和无意义的空格去掉
        old_path=os.path.join(resource_dir, matched_file)
        safe_filename=matched_file.replace(' ', '').replace('_','')
        new_path=os.path.join(resource_dir, safe_filename)
        os.rename(old_path,new_path)
        processed_files.add(safe_filename)
        if data_type=='2':
        #插入图片的md语法
            return f"\n![{safe_filename}]({safe_filename})\n"
        if data_type=='4':
            #插入视频的md语法
            return f'\n<video src="{safe_filename}" controls width="600"></video>\n'
        if data_type=='8' and safe_filename.endswith(IMAGE_EXTENSIONS):
            #data-type是8但文件后缀还是属于图片那么还应该用图片的markdown语法![](),而不是文件链接[]()
            return f"\n![{safe_filename}]({safe_filename})\n"
        return f"\n[{safe_filename}]({safe_filename})\n"


def html_to_markdown_with_resources(html:str, resource_dir:str)->str:
    '''将html内的内容转为MarkDown文本'''
    soup=BeautifulSoup(html, "html.parser")
    processed_files=set()
    #微信待办
    for todo in soup.find_all("wn-todo"):
        checked=todo.get("checked", "0")
        text=todo.get_text(strip=True)
        prefix="- [x]" if checked == "1" else "- [ ]"
        todo.replace_with(f"\n{prefix} {text}\n")

    #位置其他链接卡片（从<u>提取）,其实压根不会显示,可能是只有在点击发送请求后才嵌入
    for u in soup.find_all("u"):
        text=u.get_text(strip=True)
        if text.startswith("http://") or text.startswith("https://"):
            href=text.replace("&amp;", "&")
            u.replace_with(f"\n[{href}]({href})\n")

    #html里的object资源（图片,文件，视频）
    for obj in soup.find_all("object"):
        md_res=resolve_object_resource(obj, resource_dir, processed_files)
        obj.replace_with(md_res)
    md_text=md(
        str(soup),
        heading_style="ATX",
        bullets="-",
        strip=["script", "style"],
        wrap=False,
    )
    return clean_weixin_markdown(md_text)


def export_weixin_note(resource_dir:str,md_name:str="Notes.md")->str:
    '''
    将微信笔记HTML导出为Markdown格式
    Args:
        resource_dir:包含.htm和其他资源文件的目录
        md_name:生成的Markdown文件名
    Returns: 生成的Markdown文件完整路径
    '''
    if not os.path.isdir(resource_dir):
        raise NotADirectoryError(f"目录不存在:{resource_dir}")
    html_files=[
        os.path.join(resource_dir, f)
        for f in os.listdir(resource_dir)
        if f.lower().endswith(".htm")]
    if not html_files:
        raise FileNotFoundError("未找到 .htm 文件")
    html_path=html_files[0]
    with open(html_path,"r",encoding="utf-8") as f:
        html=f.read()
    md_text=html_to_markdown_with_resources(html,resource_dir)
    output_md_path=os.path.join(resource_dir,md_name)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    return output_md_path