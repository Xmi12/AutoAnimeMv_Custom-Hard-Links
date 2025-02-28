#!/usr/bin/python3
#coding:utf-8
from sys import argv,executable #获取外部传参和外置配置更新
from os import environ,path,name,makedirs,listdir,link,remove,removedirs,renames # os操作
from time import sleep,strftime,localtime,time # 时间相关
from datetime import datetime # 时间相减用
from re import findall,match,search,sub,I # 匹配相关
from shutil import move # 移动File
from ast import literal_eval # srt转化
from zhconv import convert # 繁化简
from urllib.parse import quote,unquote # url encode
from requests import get,post,exceptions # 网络部分
from urllib.request import getproxies  # 获取系统代理
#from random import randint # 随机数生成
#from threading import Thread # 多线程
from importlib import import_module # 动态加载模块
#Start 开始部分进行程序的初始化 

def Start_PATH(**kwargs) -> dict:
    '''初始化'''
    # 版本 数据库缓存 Api数据缓存 Log数据集 分隔符
    global Versions,AimeListCache,BgmAPIDataCache,TMDBAPIDataCache,LogData,Separator,Proxy,TgBotMsgData,PyPath,CUSTOM_LINK_DIR
    Versions = '3.(4.5).6'
    AimeListCache = None
    CUSTOM_LINK_DIR = '这里换成自定义硬链接路径'
    BgmAPIDataCache = {}
    TMDBAPIDataCache = {}
    LogData = f'\n\n[{strftime("%Y-%m-%d %H:%M:%S",localtime(time()))}] INFO: Running....'
    Separator = '\\' if name == 'nt' else '/'
    TgBotMsgData = ''
    PyPath = __file__.replace('AutoAnimeMv.py','').strip(' ')

    global USEMODULE,USEPROXY,USESYSPROXY,HTTPPROXY,HTTPSPROXY,ALLPROXY,USEBGMAPI,USETMDBAPI,USELINK,LINKFAILSUSEMOVEFLAGS,USETITLTOEP,PRINTLOGFLAG,RMLOGSFLAG,USEBOTFLAG,TIMELAPSE,SEEPSINGLECHARACTER,JELLYFINFORMAT,NOTLOADEXTLIST,MANDATORYCOVER,NETERRRECTRYTIMS,APIREQUESTSONLYUSECH,USEANIMETAG
    USEMODULE = None
    USEPROXY = False # 使用代理
    USESYSPROXY = False # 使用系统代理
    HTTPPROXY = '' # Http代理
    HTTPSPROXY = '' # Https代理
    ALLPROXY = '' # 全部代理
    USEBGMAPI = True # 使用BgmApi
    USETMDBAPI = True # 使用TMDBApi
    USELINK = True # 使用硬链接开关
    JELLYFINFORMAT = False # jellyfin 使用 ISO/639 标准 简体和繁体都使用chi做标识\
    USETITLTOEP = False # 给每个番剧视频加上番剧Title 
    LINKFAILSUSEMOVEFLAGS = False #硬链接失败时使用MOVE
    PRINTLOGFLAG = True if __name__ == '__main__' else False# 打印log开关
    RMLOGSFLAG = 7 # 日志文件超时删除,填数字代表删除多久前的
    USEBOTFLAG = False # 使用TgBot进行通知
    TIMELAPSE = 0 # 延时处理番剧
    SEEPSINGLECHARACTER = False # SE EP单字符模式 01 -> 1
    NOTLOADEXTLIST = [] # 模块排除列表,格式 exmaple.py,XXXX.py + ,
    MANDATORYCOVER = False # 强制覆盖文件
    NETERRRECTRYTIMS = 1 # 网络请求错误时的重试次数
    APIREQUESTSONLYUSECH = False # Api请求只搜索中文部分
    USEANIMETAG = False # 使用番剧tag,带有anime标签的文件才会处理

    Auxiliary_READConfig()
    Auxiliary_ApplyConfig()
    Auxiliary_Log((f'当前工具版本为{Versions}',f'当前操作系统识别码为{name},posix/nt/java对应linux/windows/java虚拟机'),'INFO')
    if int(TIMELAPSE) != 0:
        Auxiliary_Log(f'正在{TIMELAPSE}秒延时中')
        sleep(int(TIMELAPSE))
    if USEMODULE == True:
        Auxiliary_LoadModule()
    if kwargs != {}:
        for i in kwargs:
            exec(f'global {i};{i} = {kwargs[i]}')
    return globals()

def AUxiliary_GetTag():
    '''获取Tag信息,判断处理模式'''
    def A(tag):
        if tag == 'anime':
            global USEANIMETAG
            USEANIMETAG = False  
        elif (X := search(r'AAM-(.*)',tag,flags=I)) != None:
                global animename
                animename = X.group(1)
                Auxiliary_Log(f'tag中指定了番剧名称 > {animename}')

    if tag and tag != '':
        if ',' not in tag :
            A(tag)
        elif ',' in tag:    
            for i in tag.split(','):
                A(i)
    if USEANIMETAG == True:
        Auxiliary_Exit('已开启USEANIMETAG配置,但不存在番剧Tag,正常退出')

def Start_GetArgv():
    '''获取参数,判断处理模式'''

    if len(argv) != 1:
        Key = ['filepath','filename','number','categoryname','animename','tag']
        # 
        ComKey = ['help','update','fixSE']
        for i in Key:
            globals()[i] = None
            try:
                globals()[i] = (X := argv[argv.index(f'--{i}')+1])
                Auxiliary_Log(f'{i} < {X}')
            except ValueError:
                pass  

        #Auxiliary_Log(f'filepath:{filepath} filename:{filename} number:{number} categoryname:{categoryname}')
        if filepath and path.exists(filepath):  
            AUxiliary_GetTag()  
            if (filename and number):
                return filepath,filename,number
            else:
                return filepath
        elif argv[1] in ComKey:
            pass
    Auxiliary_Help()
    
        
# Processing 进行程序的开始工作,进行核心处理
def Processing_Mode(ArgvData:list):
    '''模式选择'''

    ArgvNumber = len(ArgvData)
    global Path,CategoryName
    Path = filepath
    CategoryName = categoryname
    if path.exists(Path) == True:
        # 批处理模式(非分类|分类) or Qb下载模式
        FileListTuporList = Auxiliary_ScanDIR(Path) if ArgvNumber <= 2 or (ArgvData[2] != '1') else [ArgvData[1]]
        Auxiliary_DeleteLogs()
        if CategoryName :
            Auxiliary_Log(f'当前分类 >> {CategoryName}')

        if type(FileListTuporList) == tuple:
            return FileListTuporList # 文件列表元组(视频文件列表,字幕文件列表)
        else:
            for i in FileListTuporList:
                if path.isfile(f'{Path}{Separator}{i}') == False:
                    Auxiliary_Log(f'{Path}{Separator}{i} 不存在的文件','WARNING')
                    FileListTuporList.remove(i)
            if FileListTuporList != []:
                return FileListTuporList  # 元组中唯一有效的文件列表
            Auxiliary_Exit('没有有效的番剧文件')
    else:
        Auxiliary_Exit(f'不存在 {Path} 目录')
   
def Processing_Main(LorT):
    '''核心处理'''

    if type(LorT) == tuple: # (视频文件列表,字幕文件列表)
        for FileList in LorT:
            for File in FileList:
                Auxiliary_Log('-'*80,'INFO')
                flag = Processing_Identification(File)
                if flag == None:
                    break
                SE,EP,RAWSE,RAWEP,RAWName = flag
                if Auxiliary_FileType(File) != 'ASS':
                    ASSList = Auxiliary_IDEASS(RAWName,RAWSE,RAWEP,LorT[1])
                ApiName = Auxiliary_Api(RAWName)
                Sorting_Mv(File,RAWName,SE,EP,ASSList,ApiName)
    else:# 唯一有效的文件列表
        for File in LorT:
            flag = Processing_Identification(File)
            if flag == None:
                break
            SE,EP,RAWSE,RAWEP,RAWName = flag
            ApiName = Auxiliary_Api(RAWName)
            Sorting_Mv(File,RAWName,SE,EP,None,ApiName)

def Processing_Identification(File:str):
    '''识别'''

    NewFile = Auxiliary_RMSubtitlingTeam(Auxiliary_RMOTSTR(Auxiliary_UniformOTSTR(File)))# 字符的统一加剔除
    AnimeFileCheckFlag = Auxiliary_AnimeFileCheck(NewFile)
    if AnimeFileCheckFlag == True:
        Auxiliary_Log('-'*80,'INFO')
        try:
            RAWEP = Auxiliary_IDEEP(NewFile)
        except:
            Auxiliary_Log(f'{File}文件无法处理故跳过','WARNIG')
            return None
        else:
            Auxiliary_Log(f'匹配出的剧集 ==> {RAWEP}','INFO')
            RAWName = Auxiliary_IDEVDName(NewFile,RAWEP)
            EP = '0' + RAWEP if (len(RAWEP) < 2 or ( '.' in RAWEP and RAWEP[0] != '0')) and (SEEPSINGLECHARACTER == False) else RAWEP# 美化剧集
            if '.' in RAWEP or RAWEP == '0' or RAWEP == '00':
                SE = '00' if SEEPSINGLECHARACTER == False else '0'
                RAWSE = ''
                Auxiliary_Log(f'特殊剧季 ==> {SE}','INFO')
                SeasonMatchData = r'(季(.*?)第)|(([0-9]{0,1}[0-9]{1})S)|(([0-9]{0,1}[0-9]{1})nosaeS)|(([0-9]{0,1}[0-9]{1}) nosaeS)|(([0-9]{0,1}[0-9]{1})-nosaeS)|(nosaeS-dn([0-9]{1}))'
                RAWName = sub(SeasonMatchData,'',RAWName[::-1],flags=I)[::-1].strip('-=')
            else:
                SE,Name,RAWSE = Auxiliary_IDESE(RAWName)
                Auxiliary_Log(f'匹配出的剧季 ==> {RAWSE}','INFO')
                RAWName = RAWName if Name == None else Name
                SE = '0' + SE if len(SE) == 1 and SEEPSINGLECHARACTER == False else SE
            if SEEPSINGLECHARACTER == True:
                SE = SE.lstrip('0')
                EP = EP.lstrip('0')
            return SE,EP,RAWSE,RAWEP,RAWName
    else:
        Auxiliary_Log(f'当前文件属于{AnimeFileCheckFlag},跳过处理','INFO')

# Sorting 进行整理工作
def Sorting_Mv(FileName,RAWName,SE,EP,ASSList,ApiName):
    '''文件处理'''

    def create_custom_link(src_path):
        if not CUSTOM_LINK_DIR or not path.exists(src_path):
            return
        try:
            relative_path = path.relpath(src_path, start=Path)
            custom_path = path.join(CUSTOM_LINK_DIR, relative_path)
            if not path.exists((custom_dir := path.dirname(custom_path))):
                makedirs(custom_dir, exist_ok=True)
            link(src_path, custom_path)
            Auxiliary_Log(f'镜像链接: {custom_path}')
        except Exception as e:
            Auxiliary_Log(f'链接失败: {str(e)}', 'WARNING')


    global CategoryName
    def FileML(src,dst):
        global TgBotMsgData
        if USELINK == True:
            try:
                link(src,dst)
                Auxiliary_Log(f'Link-{dst} << {src}','INFO')
                create_custom_link(dst)
            except OSError as err:
                if '[WinError 1]' in str(err):
                    Auxiliary_Log('当前文件系统不支持硬链接','ERROR')
                    if LINKFAILSUSEMOVEFLAGS == True:
                        move(src,dst)
                        Auxiliary_Log(f'Move-{src} << {dst}')
                else:
                    Auxiliary_Exit(err)
        else:
            move(src,dst)
            Auxiliary_Log(f'Move-{dst} << {src}')
            create_custom_link(dst)
    
    CategoryName = CategoryName if CategoryName else ''
    NewDir = f'{Path}{Separator}{CategoryName}{Separator}{ApiName}{Separator}Season{SE}{Separator}' if ApiName != None else f'{Path}{Separator}{CategoryName}{Separator}{RAWName}{Separator}Season{SE}{Separator}'
    NewName = f'S{SE}E{EP}' if USETITLTOEP != True else f'S{SE}E{EP}.{ApiName}'
    if path.exists(NewDir) == False:
        makedirs(NewDir)
    else:
        Auxiliary_Log(f'{NewDir}已存在','INFO')
    if ASSList != None:
        for ASSFile in ASSList:
            FileType = path.splitext(ASSFile)[1].lower()
            NewASSName = NewName + Auxiliary_ASSFileCA(ASSFile)
            if path.isfile((X := f'{NewDir}{NewASSName}{FileType}')) == False or MANDATORYCOVER == True:
                FileML(f'{Path}{Separator}{ASSFile}',X)
            else:
                Auxiliary_Log(f'{NewDir}{NewASSName}{FileType}已存在,故跳过','WARNING')
    FileType = path.splitext(FileName)[1].lower()
    NewName = NewName + Auxiliary_ASSFileCA(FileName) if FileType == '.ass' or FileType == '.str' else NewName
    if path.isfile((X := f'{NewDir}{NewName}{FileType}')) == False or MANDATORYCOVER == True:
        FileML(f'{Path}{Separator}{FileName}',X)
    else: 
        Auxiliary_Log(f'{X}已存在,故跳过','WARNING')

# Auxiliary 其他辅助
def Auxiliary_Help(): # Help 
    global HelpMessages
    Logo = '''     
     █████╗ ██╗   ██╗████████╗ ██████╗  █████╗ ███╗   ██╗██╗███╗   ███╗███████╗███╗   ███╗██╗   ██╗
    ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔══██╗████╗  ██║██║████╗ ████║██╔════╝████╗ ████║██║   ██║
    ███████║██║   ██║   ██║   ██║   ██║███████║██╔██╗ ██║██║██╔████╔██║█████╗  ██╔████╔██║██║   ██║
    ██╔══██║██║   ██║   ██║   ██║   ██║██╔══██║██║╚██╗██║██║██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║╚██╗ ██╔╝
    ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║  ██║██║ ╚████║██║██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║ ╚████╔╝ 
    ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═══╝                                                                                            
    '''
    HelpMessages = '\n* 欢迎使用AutoAnimeMv，这是一个番剧自动识别剧名剧集+自动重命名+自动整理的工具\n* Github URL：https://github.com/Abcuders/AutoAnimeMv\n* '
    print(Logo + '\n' + '-'*100 +  HelpMessages)
    quit()

def Auxiliary_LoadModule():
    ModuleFileList = []
    if path.exists('./Ext') == True:
        for FileName in listdir('./Ext'):
            File = path.splitext(FileName)
            if File[-1] == '.py' or File[-1] == '.PY':
                if File[0] in NOTLOADEXTLIST:
                    Auxiliary_Log(f'排除模块：{File[0]}')
                else:
                    Module = import_module(f'Ext.{File[0]}')
                    Auxiliary_Log(f'模块 << {File[0]}-v{Module.Versions}')
                    if '#' + File[0] in ConfigMagdict:
                        Module.main(globals(),ConfigMagdict[f'#{File[0]}'])
                    else:
                        Module.main(globals())
                    ModuleFileList.append(File[0])
                    # AAF = []
                    # for i in Module.ApplyAccessFun:
                    #     AAF.append(globals()[i])
                    # ReturnFun = Module.main(AAF)
                    #ModuleFileList[File[0]] = {'Versions':Module.Versions,'ApplyAccessFun':Module.ApplyAccessFun,'ApplyChangeFun':Module.ApplyChangeFun,'Module':Module,'ReturnFun':ReturnFun}
            #elif File[-1] == '.ini' or File[-1] == '.INI':
        if ModuleFileList != {}:
            Auxiliary_Log(f'加载{len(ModuleFileList)}个可加载模块 >> {ModuleFileList}')       
        else:
            Auxiliary_Log('无扩展')
    else:
        Auxiliary_Log('不存在扩展文件夹 ./Ext')

def Auxiliary_READConfig():
    '''读取外置Config.ini文件并更新'''

    global ConfigMagdict
    if path.isfile((X := f'{PyPath}{Separator}config.ini')):
        with open(X,'r',encoding='UTF-8') as ff:
            Auxiliary_Log('正在读取外置ini文件','INFO')
            ConfigMagdict = {}
            for i in ff.readlines():
                i = i.strip('\n') 
                if findall(r'\[(#.*?)\]',i) != []:
                    KeyName = findall(r'\[(#.*?)\]',i)[0]
                    ConfigMagdict[KeyName] = {}
                elif i != '' and i[0] != '#':
                    ConfigItem = i.split("=",1)
                    ConfigMagdict[KeyName][ConfigItem[0].strip('- ')] = ConfigItem[1].strip('- ')
        if ConfigMagdict != {} or ('#Config' in ConfigMagdict and ConfigMagdict['#Config'] != {}):
            Auxiliary_Log(f'ConfigMagdict:{ConfigMagdict}')
        else:
            Auxiliary_Log('外置ini文件没有配置','WARNING')
            del globals()[ConfigMagdict]

def Auxiliary_ApplyConfig():
    if 'ConfigMagdict' in globals() and '#Config' in ConfigMagdict:
        for ConfigName in ConfigMagdict['#Config']:
            if ConfigName == 'CUSTOM_LINK_DIR':
                global CUSTOM_LINK_DIR
                CUSTOM_LINK_DIR = ConfigValue.strip()
                try:
                    if CUSTOM_LINK_DIR:
                        if not path.exists(CUSTOM_LINK_DIR):
                            makedirs(CUSTOM_LINK_DIR, exist_ok=True)
                except Exception as e:
                    CUSTOM_LINK_DIR = ''
                continue

            ConfigValue = ConfigMagdict['#Config'][ConfigName]
            try:
                exec(f'global {ConfigName};{ConfigName} = {literal_eval(ConfigValue)}')
            except:
                exec(f'global {ConfigName};{ConfigName} = "{ConfigValue}"')
        Auxiliary_PROXY()

def Auxiliary_Log(Msg:str,MsgFlag='INFO',flag=None,end='\n'):
    '''日志'''

    global LogData,PRINTLOGFLAG
    Msg = Msg if type(Msg) == tuple else (Msg,)
    for OneMsg in Msg:
        Msg = f'[{strftime("%Y-%m-%d %H:%M:%S",localtime(time()))}] {MsgFlag}: {OneMsg}'
        if PRINTLOGFLAG == True or flag == 'PRINT':
            print(Msg,end=end)         
        LogData = '' + Msg if 'LogData' not in globals() else LogData + '\n' + Msg

def Auxiliary_DeleteLogs():
    '''日志清理'''

    RmLogsList = []
    if RMLOGSFLAG != False and 'LogsFileList' in globals() and LogsFileList != []:
        ToDay = datetime.strptime(datetime.now().strftime('%Y-%m-%d'),"%Y-%m-%d").date()
        for Logs in LogsFileList:
            LogDate =  datetime.strptime(Logs.strip('.log'),"%Y-%m-%d").date()
            if (ToDay - LogDate).days >= int(RMLOGSFLAG):
                remove(f'{Path}{Separator}{Logs}')
                RmLogsList.append(Logs)
        if RmLogsList != []:
            Auxiliary_Log(f'清理了保存时间达到和超过{RMLOGSFLAG}天的日志文件 << {RmLogsList}')

def Auxiliary_WriteLog():
    '''写log文件'''

    LogPath = filepath if 'filepath' in globals() and path.exists(filepath) == True else PyPath
    if LogPath == PyPath:
        Auxiliary_Log(f'Log文件保存在工具目录下','WARNING')
    with open(f'{LogPath}{Separator}{strftime("%Y-%m-%d",localtime(time()))}.log','a+',encoding='UTF-8') as LogFile:
        LogFile.write(LogData)

def Auxiliary_UniformOTSTR(File):
    '''统一意外字符'''

    NewFile = convert(File,'zh-hans')# 繁化简
    NewUSTRFile = sub(r',|，| ','-',NewFile,flags=I) 
    NewUSTRFile = sub(r'[^a-z0-9\s&/:：.\-\(\)（）《》\u4e00-\u9fa5\u3040-\u309F\u30A0-\u30FF\u31F0-\u31FF°ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]','=',NewUSTRFile,flags=I)
    #异种剧集统一
    OtEpisodesMatchData = [r'第(\d{1,4})集',r'(\d{1,4})集',r'第(\d{1,4})话',r'(\d{1,4})END',r'(\d{1,4}) END',r'(\d{1,4})E']
    for i in OtEpisodesMatchData:
        i = f'[^0-9a-z]{i}[^0-9a-z]'
        if search(i,NewUSTRFile,flags=I) != None:
            a = search(i,NewUSTRFile,flags=I)
            NewUSTRFile = NewUSTRFile.replace(a.group(),'='+a.group(1).strip('\u4e00-\u9fa5')+'=')
    return NewUSTRFile

def Auxiliary_RMOTSTR(File):
    '''剔除意外字符'''

    global FuzzyMatchData
    global PreciseMatchData
    NewPSTRFile = File
    #匹配待去除列表
    FuzzyMatchData = [r'(.*?|=)月新番(.*?|=)',r'\d{4}.\d{2}.\d{2}',r'20\d{2}',r'v[2-9]',r'\d{4}年\d{1,2}月番']
    #精准待去除列表
    PreciseMatchData = [r'仅限港澳台地区',r'年龄限制版',r'国漫',r'x264',r'1080p',r'720p',r'4k',r'\(-\)',r'（-）']
    for i in PreciseMatchData:
        NewPSTRFile = sub(r'%s'%i,'=',NewPSTRFile,flags=I)
    for i in FuzzyMatchData:
        NewPSTRFile = sub(i,'=',NewPSTRFile,flags=I)
    return NewPSTRFile

def Auxiliary_IDESE(File):
    '''识别剧季并截断Name'''

    SeasonMatchData = r'(季(.*?)第)|(([0-9]{0,1}[0-9]{1})S)|(([0-9]{0,1}[0-9]{1})nosaeS)|(([0-9]{0,1}[0-9]{1}) nosaeS)|(([0-9]{0,1}[0-9]{1})-nosaeS)|(nosaeS-dn([0-9]{1}))|(nosaeS-dr([0-9]{1}))'
    if (X := findall(SeasonMatchData,File[::-1],flags=I)) != []:
        SEData = X
        SENamelist = []
        SEList = []
        for sedata in SEData:
            for se in sedata:# 取值
                if se != '' and se.isnumeric() == False:
                    SENamelist.append(se[::-1])
                #elif len(se) == 1:
                #    SEList.append(se)
                elif se.isnumeric() == True: # 判断数字
                    SEList.append(se)
        for i in SENamelist:# 截断Name
            File = sub(r'%s.*'%i,'',File,flags=I).strip('=') #通过剧季截断文件名
        for i in range(len(SEList)):
            if SEList[i].isdecimal() == True: # 判断纯数字
                SE = SEList[i][::-1]
            elif '\u0e00' <= SEList[i] <= '\u9fa5':# 中文剧季转化
                digit = {'一':'01', '二':'02', '三':'03', '四':'04', '五':'05', '六':'06', '七':'07', '八':'08', '九':'09','壹':'01','贰':'02','叁':'03','肆':'04','伍':'05','陆':'06','柒':'07','捌':'08','玖':'09'}
                SE = digit[SEList[i]]
            if SE is not None:
                return SE,File,SENamelist[0]
    elif (X := findall(r'[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩⅪⅫ]',File[::-1],flags=I)) != []:
        A = {'Ⅰ':'01','Ⅱ':'02','Ⅲ':'03','Ⅳ':'04','Ⅴ':'05','Ⅵ':'06','Ⅶ':'07','Ⅷ':'08','Ⅸ':'09','Ⅹ':'10','Ⅺ':'11','Ⅻ':'12'}
        return A[X[0]],File,X[0]
    else:
        return '01',File,''

def Auxiliary_IDEEP(File):
    '''识别剧集'''

    try:
        if findall(r'[^0-9.\u4e00-\u9fa5\u0800-\u4e00]([0-9.]{1,4}-[0-9.]{1,4})[^0-9.\u4e00-\u9fa5\u0800-\u4e00]',File[::-1],flags=I) != []:
            Auxiliary_Log('剧集包不予处理','WARNING')
            raise Exception()
        elif (X := findall(r'[^0-9a-z.\u4e00-\u9fa5\u0800-\u4e00]([0-9.]{1,5})[^0-9a-uw-z.\u4e00-\u9fa5\u0800-\u4e00]',File[::-1],flags=I)) != []:
            Episodes = X[0][::-1].strip(" =-_eEv")
        else:
            Episodes = findall(r'[^0-9a-z.\u4e00-\u9fa5\u0800-\u4e00]([0-9]{1,4})[^0-9a-uw-z.\u4e00-\u9fa5\u0800-\u4e00]',File[::-1],flags=I)[0][::-1].strip(" =-_eEv")

    except IndexError:
        Auxiliary_Log('未匹配出剧集,请检查(程序目前不支持电影动漫)','WARNING')
        raise Exception()
    except :
        raise Exception()
    else:
        #Auxiliary_Log(f'匹配出的剧集 ==> {Episodes}','INFO')
        return Episodes

def Auxiliary_RMSubtitlingTeam(File):
    '''剔除字幕组信息'''

    #File = File.strip('=')
    if File[0] == '《':# 判断有无字幕组信息
        File = sub(r'《|》','',File,flags=I) 
    else:
        File = sub(r'^=.*?=','',File,flags=I)
    return File

def Auxiliary_IDEVDName(File,RAWEP): 
    '''识别剧名'''

    #VDName = sub(r'.*%s'%RAWEP[::-1],'',File[::-1],count=0,flags=I).strip('=-=-=-')[::-1]
    VDName = search(r'[=|-]%s[=|-](.*)'%RAWEP[::-1],File[::-1],flags=I).group(1).strip('=-=-=-')[::-1]
    Auxiliary_Log(f'通过剧集截断文件名 ==> {VDName}','INFO')
    return VDName

def Auxiliary_IDEASS(File,SE,EP,ASSList):
    '''识别当前番剧视频的所属字幕文件'''

    ASSFileList = []
    for ASSFile in ASSList:
        ASSName = Auxiliary_UniformOTSTR(ASSFile)
        ASSEP = Auxiliary_IDEEP(ASSName)
        if File in ASSName and EP == ASSEP and SE in ASSName:
            ASSFileList.append(ASSFile)
    ASSFileList = None if ASSFileList == [] else ASSFileList
    return ASSFileList

def Auxiliary_FileType(FileName): 
    '''识别文件类型'''

    SuffixList = {'.ass':'ASS','.srt':'ASS','.mp4':'MP4','.mkv':'MP4','.log':'LOG'}
    for FileType in SuffixList:
        if match(FileType[::-1],FileName[::-1],flags=I) != None:
            try :
                return SuffixList[FileType.lower()]
            except :
                Auxiliary_Exit('文件类型不正确')

def Auxiliary_ScanDIR(Dir,Flag=0) -> list: 
    '''扫描文件目录,返回文件列表'''

    def Scan(File):
        for ii in SuffixList:
                if match(ii[::-1],File[::-1],flags=I) != None:
                    if ii == '.ass' or ii == '.srt':
                        AssFileList.append(File)
                    elif ii == '.log':
                        LogsFileList.append(File)
                    else:
                        VDFileList.append(File)

    global LogsFileList
    SuffixList = ['.ass','.srt','.mp4','.mkv','.log']
    AssFileList = []
    VDFileList = []
    LogsFileList = []
    for File in listdir(Dir):# 扫描目录,并按文件类型分类
        if Flag == 0 and search(r'S\d{1,2}E\d{1,4}',File,flags=I) == None:
            Scan(File)
        elif Flag == 1 and search(r'S\d{1,2}E\d{1,4}',File,flags=I) != None:
            Scan(File)

    if  VDFileList != []:# 判断模式,处理字幕还是视频
        if AssFileList != []:
            Auxiliary_Log((f'发现{len(AssFileList)}个字幕文件 ==> {AssFileList}',f'发现{len(VDFileList)}个视频文件 ==> {VDFileList}'),'INFO')
            return VDFileList,AssFileList
        else:
            Auxiliary_Log(f'发现{len(VDFileList)}个视频文件,没有发现字幕文件 ==> {VDFileList}','INFO')
            return VDFileList
    elif AssFileList != []:
        Auxiliary_Log((f'没有发现任何番剧视频文件,但发现{len(AssFileList)}个字幕文件 ==> {AssFileList}','只有字幕文件需要处理'),'INFO')
        return AssFileList
    else:
        Auxiliary_Exit('没有任何番剧文件')

def Auxiliary_AnimeFileCheck(File):
    '''检查番剧文件'''

    Checklist = ['OP','CM','SP','PV']
    for i in Checklist:
        if search(f'[-=]{i}[-=]',File,flags=I) != None:
            return i
    return True         

def Auxiliary_ASSFileCA(ASSFileName):
    '''字幕文件的语言分类'''

    SubtitleList = [['简','簡','簡體','sc','chs','GB'],['繁','tc','cht','BIG5'],['日','jp']]
    for i in range(len(SubtitleList)):
        for ii in SubtitleList[i]:
            if search(f'[^0-9a-z]{ii[::-1]}[^0-9a-z]',ASSFileName[::-1],flags=I) != None:
                if i == 0:
                    return '.chs' if JELLYFINFORMAT == False else '.简体中文.chi'
                elif i == 1:
                    return '.cht' if JELLYFINFORMAT == False else '.繁体中文.chi'
                elif i == 2:
                    return '.jp'
    return '.other'

def Auxiliary_PROXY(): 
    '''代理'''
    if USEPROXY == True:
        global HTTPPROXY
        global HTTPSPROXY
        global ALLPROXY
        Auxiliary_Log('代理功能开启')
        if USESYSPROXY == True:
            Auxiliary_Log('使用系统代理')
            HTTPPROXY,HTTPSPROXY,a = X if (X:= tuple(getproxies().values())) != () else ('','','')
        environ['http_proxy'] = HTTPPROXY 
        environ['https_proxy'] = HTTPSPROXY 
        environ['all_proxy'] = ALLPROXY 
        
        

def Auxiliary_Http(Url,flag='GET',json=None):
    '''网络'''
     
    headers = {'User-Agent':f'Abcuders/AutoAnimeMv/{Versions}(https://github.com/Abcuders/AutoAnimeMv)'}
    if 'themoviedb' in Url:
        headers['Authorization'] = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0MjkxYzA0NGYyZTNmMThhYzQ3NzNjNzU1YzM3NzA5OSIsInN1YiI6IjY0MjZlMTg1YTNlNGJhMDExMTQ5OGI2MSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Q0Rn4QdnCelhzozE07jgUQwJFzdJrLXGhaSBphnzYuQ"
    for i in range(int(NETERRRECTRYTIMS)+1):    
        try:
            if flag != 'GET':
                HttpData = post(Url,json,headers=headers) 
            else:
                HttpData = get(Url,headers=headers)
            if HttpData.status_code == 200:
                return HttpData.text.replace(r'\/',r'/')
        except exceptions.ConnectionError:
            Auxiliary_Log(f'访问 {Url} 失败,未能获取到内容,请检查您是否启用了系统代理,如是则您应该在此工具中配置代理信息,否则您则需要检查您的网络能否访问','WARING') 
        except Exception as err:
            Auxiliary_Log(f'访问 {Url} 失败,未能获取到内容,请检查您的网络 {err}','WARING')    
        else:
            Auxiliary_Log('HttpData Status Code != 200','WARING')
        Auxiliary_Log(f'第{i+1}/{int(NETERRRECTRYTIMS)+1}次尝试失败','WARING')
    Auxiliary_Exit('网络错误导致番剧处理失败')

def Auxiliary_Api(Name):   
    def BgmApi(Name):
        '''BgmApi相关,返回一个标准的中文名称'''

        global USEBGMAPI,BgmAPIDataCache
        if USEBGMAPI == True:
            if Name not in BgmAPIDataCache:
                try:
                    BgmApiData = literal_eval(Auxiliary_Http(f"https://api.bgm.tv/search/subject/{Name}?type=2&responseGroup=small&max_results=1"))
                except:
                    Auxiliary_Log(f'BgmApi没有检索到关于 {Name} 内容','WARNING')
                    return None
                else:
                    if BgmApiData != None:
                        ApiName = unquote(BgmApiData['list'][0]['name_cn'],encoding='UTF-8',errors='replace') if unquote(BgmApiData['list'][0]['name_cn'],encoding='UTF-8',errors='replace') != '' else unquote(BgmApiData['list'][0]['name'],encoding='UTF-8',errors='replace')
                        ApiName = sub('第.*?季','',ApiName,flags=I).strip('- []【】 ')
                        Auxiliary_Log(f'{ApiName} << bgmApi查询结果')
                        BgmAPIDataCache[Name] = ApiName
                        return ApiName
                    else:
                        return None
            else:
                Auxiliary_Log(f'{BgmAPIDataCache[Name]} << bgmApi缓存查询结果')
                return BgmAPIDataCache[Name]
        else:
            Auxiliary_Log('没有使用BgmApi进行检索')
            return None

    def TMDBApi(Name): 
        '''TMDBApi相关,返回一个标准的中文名称'''

        global USETMDBAPI,TMDBAPIDataCache
        if USETMDBAPI == True:
            if Name not in TMDBAPIDataCache:
                TMDBApiData = literal_eval(Auxiliary_Http(f'https://api.themoviedb.org/3/search/tv?query={Name}&include_adult=true&language=zh&page=1').replace('false','False').replace('true','True').replace('null','None'))
                if TMDBApiData['results'] != []:
                    for MDBApiTV in TMDBApiData['results']:
                        ApiName = MDBApiTV['name']
                        ApiName = sub('第.*?季','',ApiName,flags=I).strip('- []【】 ')
                        Auxiliary_Log(f'{ApiName} << TMDBApi查询结果')
                        TMDBAPIDataCache[Name] = ApiName
                        return ApiName
                else:
                    Auxiliary_Log(f'TMDBApi没有检索到关于 {Name} 内容','WARNING')
                    return None
            else:
                Auxiliary_Log(f'{TMDBAPIDataCache[Name]} << TMDBApi缓存查询结果')
                return TMDBAPIDataCache[Name]
        else:
            Auxiliary_Log('没有使用TMDBApi进行检索')
            return None
    
    if 'animename' in globals() and animename not in ['',None]:
        Auxiliary_Log(f'使用指定的番剧名称 > {animename}')
        return animename
    else:
        if APIREQUESTSONLYUSECH and (X := search(r'([\u4e00-\u9fa5]+)',Name.replace('=','').replace('-',''),flags=I)) != None:#获取匹配到的汉字
            Name = X.group(1) 
            BGMApiName = BgmApi(Name)
            TMDBApiName = TMDBApi(BGMApiName if BGMApiName != None else Name)
                
        else:
            BGMApiName = BgmApi(Name)
            TMDBApiName = TMDBApi(BGMApiName if BGMApiName != None else Name)

        if BGMApiName == None and TMDBApiName == None:
            if USEBGMAPI == True or USETMDBAPI == True:
        #        Auxiliary_Log('Api识别失败现在进行额外的API识别')
                Auxiliary_Exit('Api识别失败')
        #        StrList = Name.split('=')
        #    else:
        #        ApiName = None
        else:
            ApiName = TMDBApiName if TMDBApiName != None else BGMApiName
        return ApiName.replace(' ','') if ApiName != None else ApiName

def Auxiliary_Exit(LogMsg):
    '''因可预见错误离场'''

    Auxiliary_Log(LogMsg,'EXIT',flag='PRINT')
    exit()

if __name__ == '__main__':
    start = time()
    try:
        Start_PATH()
        ArgvData = Start_GetArgv()
        Processing_Main(Processing_Mode(ArgvData))
    except Exception as err:
        Auxiliary_Log(f'没有预料到的错误 > {err}','ERROR',flag='PRINT')
    else:
        end = time()
        Auxiliary_Log(f'一切工作已经完成,用时{end - start}','INFO',flag='PRINT')
    finally:
        if 'HelpMessages' not in globals():
            Auxiliary_WriteLog()
